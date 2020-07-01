import json
import os

from pathlib import Path
from shutil import copyfile
from subprocess import run, CompletedProcess
from tempfile import NamedTemporaryFile
from typing import Dict, Tuple, Any, Union, IO, Final

here: Final[str] = os.path.dirname(os.path.realpath(__file__))
serialize_py: Final[str] = f'{here}/serialize.py'
atbd_tex: Final[str] = f'{here}/ATBD.tex'
main_bib: Final[str] = 'main.bib'
encoding: Final[str] = 'utf8'


class JsonToLatexException(Exception):
    pass


def json_to_latex(atbd_doc: Dict, tmp_dir: str) -> Tuple[str, str]:
    """
    Serialize atbd json to latex. This simply wraps the prototype shell script originally from
    https://github.com/developmentseed/nasa-apt/blob/eb0b6bc897efa29284dd11b4e46b085f388d9743/ecs/tex/serialize.py

    :param atbd_doc: atbd json document
    :type atbd_doc: dict
    :param tmp_dir: working directory
    :type tmp_dir: str
    :return: latex filename, .bib filename (caller should cleanup both files and tmp directory)
    :rtype: Tuple[str, str]
    :raises: JsonToLatexException: when the serialize script fails.
    """

    # serialize.py expects this template file, so copy it into tmp_dir.
    copyfile(atbd_tex, f'{tmp_dir}/ATBD.tex')

    json_fp: IO[str]
    with NamedTemporaryFile(dir=tmp_dir, mode='w') as json_fp:
        tmp_name: Final[str] = json_fp.name
        json_fp.write(json.dumps(atbd_doc))
        json_fp.flush()
        completed: Union[CompletedProcess[bytes], CompletedProcess[Any]] = run(
            args=[serialize_py, tmp_name],
            capture_output=True,
            cwd=tmp_dir,
            encoding=encoding
        )
        if completed.returncode != 0:
            # for debugging purposes, return the stdout in addition to the stderr
            raise JsonToLatexException({'stderr': completed.stderr, 'stdout': completed.stdout})
        tex_filename: Final[str] = f'{tmp_name}.tex'
        bib_filename: Final[str] = f'{tmp_dir}/{main_bib}'
        if not Path(tex_filename).exists():
            raise JsonToLatexException(f'expect intermediate file: {tex_filename}')
        if not Path(bib_filename).exists():
            raise JsonToLatexException(f'expect intermediate file: {bib_filename}')
        return tex_filename, bib_filename
