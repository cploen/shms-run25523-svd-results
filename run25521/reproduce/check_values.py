"""Coefficient reader for numerical comparisons, distinct from actual-reader test."""
import re
ROW=re.compile(r'^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+([0-9]{5})\s*$')
def read_rows(path):
 rows={}
 for line in path.read_text().splitlines():
  match=ROW.fullmatch(line)
  if match:
   assert match[5] not in rows
   rows[match[5]]=[float(match[k]) for k in [1,2,3,4]]
 return rows
