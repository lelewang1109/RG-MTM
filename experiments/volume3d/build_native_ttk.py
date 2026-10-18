"""Project-local reproducible TTK 0.9.9 adapter build (no system installation)."""
from pathlib import Path
import argparse,json,platform,subprocess,tarfile
import requests
from experiments.volume3d.prepare import ROOT,sha256

URL='https://codeload.github.com/topology-tool-kit/ttk/tar.gz/refs/tags/0.9.9'
ARCHIVE_SHA256='f7ebfdf77d0276a1c698e25286a36989cc4375df6b92489a2ccfaa47b4ff7ff1'


def build(record_existing=False,parallel=6):
    work=ROOT/'tmp/volume3d';work.mkdir(parents=True,exist_ok=True)
    archive=work/'ttk-0.9.9.tar.gz';source=work/'ttk-0.9.9';binary=work/'native-build/rgmtm_ttk_volume'
    if not archive.exists():
        part=archive.with_suffix('.gz.part')
        with requests.get(URL,stream=True,timeout=(20,120)) as response:
            response.raise_for_status()
            with part.open('wb') as f:
                for chunk in response.iter_content(1024*1024):f.write(chunk)
        part.replace(archive)
    if sha256(archive)!=ARCHIVE_SHA256:raise ValueError('TTK source archive differs from the pinned experiment input')
    if not source.exists():
        with tarfile.open(archive) as package:
            for member in package.getmembers():
                if member.name.startswith('/') or '..' in Path(member.name).parts or Path(member.name).parts[0]!='ttk-0.9.9':
                    raise ValueError('unexpected path in TTK source archive')
            package.extractall(work,filter='data')
    command=['cmake','-S',str(ROOT/'experiments/volume3d/native'),'-B',str(work/'native-build'),'-G','Ninja',
        '-DTTK_SOURCE_DIR='+str(source),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_POLICY_VERSION_MINIMUM=3.5']
    if platform.system()=='Darwin':
        omp=subprocess.check_output(['brew','--prefix','libomp'],text=True).strip()
        for lang in ['C','CXX']:
            command+=['-DOpenMP_'+lang+'_FLAGS=-Xpreprocessor -fopenmp -I'+omp+'/include','-DOpenMP_'+lang+'_LIB_NAMES=omp']
        command+=['-DOpenMP_omp_LIBRARY='+omp+'/lib/libomp.dylib']
    if not record_existing:
        subprocess.run(command,check=True)
        subprocess.run(['cmake','--build',str(work/'native-build'),'--target','rgmtm_ttk_volume','--parallel',str(parallel)],check=True)
    if not binary.exists():raise FileNotFoundError(binary)
    record=dict(ttk_version='0.9.9',source_url=URL,source_archive_sha256=sha256(archive),
        native_source_sha256=sha256(ROOT/'experiments/volume3d/native/main.cpp'),
        cmake_source_sha256=sha256(ROOT/'experiments/volume3d/native/CMakeLists.txt'),
        binary_sha256=sha256(binary),build_command=command,system=platform.platform(),record_existing=record_existing,
        compiler=subprocess.check_output(['clang++','--version'],text=True) if platform.system()=='Darwin' else subprocess.check_output(['c++','--version'],text=True))
    (work/'native-build-manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k not in ['compiler','build_command']},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--record-existing',action='store_true')
    parser.add_argument('--parallel',type=int,default=6);args=parser.parse_args();build(args.record_existing,args.parallel)
