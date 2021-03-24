import os

from pathlib import Path
from subprocess import run, CompletedProcess
from typing import Any, Union, Final

here = os.path.dirname(os.path.realpath(__file__))
pdf_sh: Final[str] = f"{here}/pdf.sh"
encoding: Final[str] = "utf8"


class LatexToPDFException(Exception):
    pass


def latex_to_pdf(latex_filename: str, tmp_dir: str) -> str:
    """
    Serialize atbd latex to pdf. This simply wraps the prototype shell script originally from
    https://github.com/developmentseed/nasa-apt/blob/eb0b6bc897efa29284dd11b4e46b085f388d9743/ecs/pdf/entrypoint.sh

    :param latex_filename: filename of latex atbd document
    :type latex_filename: str
    :param tmp_dir: working directory
    :type tmp_dir: str
    :return: filename of pdf (caller should cleanup both files and tmp directory)
    :rtype: str
    :raises LatexToPDFException: when the pdf.sh script fails.
    """
    completed: Union[CompletedProcess[bytes], CompletedProcess[Any]] = run(
        args=[pdf_sh, latex_filename],
        capture_output=True,
        cwd=tmp_dir,
        encoding=encoding,
    )
    print("Latex to PDF Output: ", completed)
    if completed.returncode != 0:
        # for debugging purposes, return the stdout in addition to the stderr
        raise LatexToPDFException(
            ({"stderr": completed.stderr, "stdout": completed.stdout})
        )

    working_name: Final[str] = Path(latex_filename).stem
    pdf_filename: Final[str] = f"{tmp_dir}/{working_name}.pdf"
    if not Path(pdf_filename).exists():
        raise LatexToPDFException(f"expect intermediate file: {pdf_filename}")
    return pdf_filename
