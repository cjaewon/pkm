import os
import shutil
import subprocess
from datetime import datetime, timezone, date, timedelta

import typer
from rich import print
from rich.console import Console

app = typer.Typer()
err_console = Console(stderr=True)


@app.command()
def new(filename: str):
  """
  Create a text file with a default metadate.
  """

  title = filename.replace('"', '\\"')

  # RFC3339
  local_now = datetime.now(timezone.utc).astimezone()
  created_at = local_now.isoformat()

  try:
    # x는 배타적 생성 모드 (Exclusive Creation)
    # 파일이 없는 경우에만 새로 만들고 쓸 수 있음.
    with open(filename, mode="x", encoding="utf-8") as f:
      f.write("---\n")
      f.write(f'title: "{title}"\n')
      f.write(f"created_at: {created_at}\n")
      f.write("---\n")

      # filename에 따옴표가 있을 수 있으므로 rich [green]을 사용함.
      print(f'Created [green]"{filename}"[/green]')
  except FileExistsError:
    err_console.print(f'[green]"{filename}"[/green] is already exists.')
    raise typer.Exit(code=1)


@app.command()
def today():
  """
  Create a text file with today's date.
  """

  new(date.today().isoformat() + ".md")


@app.command()
def tomorrow():
  """
  Create a text file with tomorrow's date.
  """

  new((date.today() + timedelta(1)).isoformat() + ".md")


@app.command()
def export(input_filepath: str, output_filepath: str):
  """
  Export a markdown file to the html or pdf file.
  """

  _, output_ext = os.path.splitext(output_filepath)

  if output_ext not in [".html", ".pdf"]:
    err_console.print(f'"{output_ext}" is not supported file extension.')
    err_console.print(f'pkm only supports ".html", ".pdf" as the ouput file.')

    raise typer.Exit(code=1)

  pandoc_bin = shutil.which("pandoc")
  typst_bin = shutil.which("typst")

  if not pandoc_bin:
    err_console.print(
      "Pandoc could not be found. pkm uses pandoc internally to convert files."
    )
    err_console.print(f"Please install Pandoc to proceed.")

    raise typer.Exit(code=1)

  if output_ext == ".pdf" and not typst_bin:
    err_console.print(
      "Typst could not be found. pkm uses typst as pandoc's pdf engine internally to convert files."
    )
    err_console.print(f"Please install Typst to proceed.")

    raise typer.Exit(code=1)


  pkm_dir = os.path.dirname(__file__)
  cmd = []

  if output_ext == ".html":
    cmd = [
      pandoc_bin,
      input_filepath,
      "-c",
      f"{pkm_dir}/export_template/pandoc_default.css",
      "-o",
      output_filepath,
      "-s",
      "--embed-resources",
    ]
  elif output_ext == ".pdf":
    cmd = [
      "pandoc",
      input_filepath,
      "--pdf-engine=typst",
      f"--template={pkm_dir}/export_template/pandoc_default_pdf.typ",
      "-o",
      output_filepath,
    ]
    
  print(f"[bold green]>>>[/bold green] {" ".join(cmd)}")

  subprocess.run(
    cmd,
    check=True,
  )


if __name__ == "__main__":
  app()