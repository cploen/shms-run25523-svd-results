"""Compile HCANA's real matrix-reader block and validate emitted matrix files.

No ROOT/HCANA build or event replay is required. Pass an existing HCANA checkout
and, optionally, nps_replay to test its working matrices as controls.
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,tempfile
ROW=re.compile(r'^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+([0-9]{5})\s*$')

def coefficient_rows(path):
    return [(m[5],[float(m[i]) for i in range(1,5)]) for line in path.read_text().splitlines() if (m:=ROW.fullmatch(line))]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hcana',required=True,type=Path)
    parser.add_argument('--nps-replay',type=Path)
    parser.add_argument('--report',type=Path)
    parser.add_argument('--matrix',type=Path,action='append',default=[],help='Additional emitted matrices to validate with the actual reader')
    args=parser.parse_args()
    repo=Path(__file__).resolve().parents[1]
    source_path=args.hcana/'src/THcHallCSpectrometer.cxx'
    source=source_path.read_text()
    start=source.index('  ifstream ifile;')
    stop=source.index('\n  return kOK;\n}',start)+len('\n  return kOK;')
    reader=source[start:stop]
    # Only the surrounding class/ROOT typedefs and Error sink are stubbed.
    # The file-reading, delimiter handling, sscanf, and return logic are verbatim.
    prefix='''#include <fstream>
#include <string>
#include <vector>
#include <iostream>
#include <iomanip>
#include <cstdio>
#include <cstdarg>
using namespace std;
using Double_t=double; using Int_t=int;
constexpr int kOK=0,kInitError=-1;
struct reconTerm { double Coeff[4]{}; int Exp[5]{}; };
struct Reader {
  int fNReconTerms=0; vector<reconTerm> fReconTerms; bool error=false;
  void Error(const char*,const char* fmt,...) {error=true; va_list ap;va_start(ap,fmt);vfprintf(stderr,fmt,ap);va_end(ap);}
  int read(const string& reconCoeffFilename) {const char* here="ReadDatabase";
'''
    suffix='''
  }
};
int main(int argc,char** argv) {
  if(argc!=2) return 3;
  Reader reader;int status=reader.read(argv[1]);
  if(status!=kOK || reader.error || !reader.fNReconTerms) return 2;
  cout << "DATA_BEGIN\\n" << setprecision(17);
  for(const auto& term:reader.fReconTerms) {
    for(double v:term.Coeff) cout << v << " ";
    for(int v:term.Exp) cout << v;
    cout << "\\n";
  }
}
'''
    results=[]
    with tempfile.TemporaryDirectory() as directory:
        work=Path(directory); cpp=work/'replay_reader.cpp';cpp.write_text(prefix+reader+suffix)
        exe=work/'replay_reader';subprocess.run(['g++','-std=c++17','-O2',str(cpp),'-o',str(exe)],check=True)
        def run(path,expected=None):
            p=subprocess.run([str(exe),str(path)],text=True,capture_output=True)
            if expected is None: return p
            assert p.returncode==0,(path,p.stdout,p.stderr)
            loaded=[]
            for line in p.stdout.split('DATA_BEGIN\n',1)[1].splitlines():
                fields=line.split();loaded.append((fields[4],[float(v) for v in fields[:4]]))
            assert loaded==expected,(path,'reader values/order differ')
            results.append({'file':str(path.relative_to(repo)) if path.is_relative_to(repo) else str(path),'terms_read':len(loaded),'exact_coefficients_and_exponents':True})
        paths=[repo/'weighted/matrices/nps_shms_newfit_25523_legacy.dat',repo/'unweighted/matrices/nps_shms_newfit_25523_unweighted.dat']
        paths.append(repo/'config/base_matrix.dat')
        paths.extend(args.matrix)
        if args.nps_replay:
            paths += [args.nps_replay/'DATFILES'/name for name in ['nps_hms_optics_5p878_ang.dat','nps_hms_optics_6p117_ang.dat','nps_hms_optics_6p667_ang.dat']]
        for path in paths:
            expected=coefficient_rows(path);assert expected;run(path,expected)
        # Reproduce the original defect and check exact delimiter requirements.
        negative=[]
        text=paths[1].read_text(); first=' ---------------------------------------------\n'
        assert text.startswith(first)
        for label,changed in [('missing_opening_separator',text[len(first):]),('two_leading_spaces',text.replace(first,'  ---------------------------------------------\n',1)),('underscores',text.replace(first,' _____________________________________________\n',1)),('missing_final_newline',text.rstrip('\n'))]:
            path=work/(label+'.dat');path.write_text(changed)
            outcome=run(path);assert outcome.returncode!=0,(label,'unexpectedly accepted')
            negative.append({'case':label,'rejected':True})
        # Compile the actual coefficient-output block from the current fitter.
        fitter=(repo/'fit_opt_matrix_gmm.C').read_text()
        a=fitter.index('  char coeffstring[100];')
        end='  cout << "wrote new coeffs file" << endl;'
        z=fitter.index(end,a)+len(end)
        writer=fitter[a:z]
        writer_source='''#include <fstream>
#include <iostream>
#include <iomanip>
#include <vector>
#include <cstdio>
using namespace std;
using Double_t=double;
int main(int argc,char** argv) {
  if(argc!=2) return 3;
  ofstream newcoeffsfile(argv[1]);
  int num_recon_terms_fit=2,num_recon_terms_xtar=1;
  vector<double> b_xptar{.125,.5},b_ytar{.25,.75},b_yptar{.375,1.},deltacoeffs_fit{0.,1.25};
  vector<int> xfpexpon_fit{0,1},xpfpexpon_fit{0,0},yfpexpon_fit{0,0},ypfpexpon_fit{0,0},xtarexpon_fit{0,0};
  vector<double> xptarcoeffs_xtar{1.5},ytarcoeffs_xtar{1.75},yptarcoeffs_xtar{2.},deltacoeffs_xtar{2.25};
  vector<int> xfpexpon_xtar{0},xpfpexpon_xtar{0},yfpexpon_xtar{0},ypfpexpon_xtar{0},xtarexpon_xtar{1};
'''+writer+'\n}\n'
        writer_cpp=work/'writer.cpp';writer_cpp.write_text(writer_source)
        writer_exe=work/'writer';subprocess.run(['g++','-std=c++17','-O2',str(writer_cpp),'-o',str(writer_exe)],check=True)
        emitted=work/'emitted.dat';subprocess.run([str(writer_exe),str(emitted)],check=True,capture_output=True)
        run(emitted,[('00000',[.125,.25,.375,0.]),('10000',[.5,.75,1.,1.25]),('00001',[1.5,1.75,2.,2.25])])
    commit=subprocess.check_output(['git','-C',str(args.hcana),'rev-parse','HEAD'],text=True).strip()
    report={'test':'verbatim HCANA ReadDatabase matrix-reader block plus verbatim current writer block','hcana_commit':commit,'reader_block_sha256':hashlib.sha256(reader.encode()).hexdigest(),'fitter_sha256':hashlib.sha256((repo/'fit_opt_matrix_gmm.C').read_bytes()).hexdigest(),'positive_cases':results,'negative_cases':negative,'full_HCANA_replay_performed':False}
    if args.report: args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
