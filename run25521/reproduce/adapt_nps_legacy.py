"""Adapt only the named upstream diagnostic macros; do not fit or change targets."""
from pathlib import Path
import sys,difflib,hashlib,json,subprocess
source=Path(sys.argv[1]);folder=Path(__file__).resolve().parent/'nps_legacy';folder.mkdir(exist_ok=True)
provenance={'repository':'https://github.com/cploen/NPS_HMS_OPTICS','commit':subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip(),'files':{}}
for axis,stem,summary in [('xptar','xpdiff','xs'),('yptar','ypdiff','ys'),('ytar','ydiff','xs')]:
 name=f'plot_{axis}_diff.C';original=(source/name).read_text();s=original
 s='#include "../../../spectrometer_config.h"\n#include <TSystem.h>\n#include <TGraphErrors.h>\n#include <TMultiGraph.h>\n#include <vector>\n'+s
 s=s.replace(f'void plot_{axis}_diff(Int_t nrun=1814,Int_t FileID=-2){{',f'void plot_{axis}_diff(Int_t nrun,const char* inputFile,const char* metadataFile,const char* outdir,const char* tag){{')
 start=s.index(' TString OpticsFile =');end=s.index('  if (NumFoil==0) return;',start)+len('  if (NumFoil==0) return;')
 s=s[:start]+''' hallc::RunMetadata metadata;
 string error;
 if (!hallc::readRunMetadata(nrun,metadata,error,metadataFile)) {cerr << error << endl;return;}
 const Int_t NumFoil=metadata.foils.size(), ndelcut=metadata.edges.size()-1;
 const Int_t RunNum=nrun, SieveFlag=metadata.sieveFlag;
 const TString OpticsID=metadata.opticsId.c_str();
 const Double_t CentAngle=metadata.angle;
 const vector<Double_t> ztar_foil=metadata.foils, delcut=metadata.edges;
 cout << "Metadata: " << NumFoil << " foils, " << ndelcut << " delta intervals" << endl;
 gSystem->mkdir(outdir,kTRUE);
'''+s[end:]
 start=s.index('   TString inputroot;');end=s.index('TFile *hroot =',start)
 assignments=f'''   TString inputroot=inputFile;
   TString outputpdf=Form("%s/%s_{stem}",outdir,tag);
   TString outputpdf1=Form("%s/%s_{stem}_{summary}",outdir,tag);
   TString outputhist=Form("%s/%s_{stem}_hist.root",outdir,tag);
'''
 if axis=='ytar':assignments+='   TString outputpdf2=Form("%s/%s_ydiff_delta",outdir,tag);\n'
 s=s[:start]+assignments+s[end:]
 s=s.replace('<9;','<11;').replace('.resize(9)','.resize(11)').replace('TGraphErrors(9,','TGraphErrors(11,')
 s=s.replace('(nys-4)*0.6*2.54','(nys-5)*1.64').replace('(nys-4)*2.54','(nys-5)*2.5')
 s=s.replace('HMS Angle','SHMS Angle')
 (folder/(name+'.original')).write_text(original);(folder/name).write_text(s)
 (folder/(name+'.diff')).write_text(''.join(difflib.unified_diff(original.splitlines(True),s.splitlines(True),fromfile='upstream/'+name,tofile='adapted/'+name)))
 provenance['files'][name]={'original_sha256':hashlib.sha256(original.encode()).hexdigest(),'adapted_sha256':hashlib.sha256(s.encode()).hexdigest()}
(folder/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
