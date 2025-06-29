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

  title = filename.replace("\"", "\\\"")

  # RFC3339
  local_now = datetime.now(timezone.utc).astimezone()
  created_at = local_now.isoformat() 

  try:
    # x는 배타적 생성 모드 (Exclusive Creation)
    # 파일이 없는 경우에만 새로 만들고 쓸 수 있음.
    with open(filename, mode="x", encoding="utf-8") as f:
      f.write("---\n")
      f.write(f"title: \"{title}\"\n")
      f.write(f"created_at: {created_at}\n") 
      f.write("---\n")

      # filename에 따옴표가 있을 수 있으므로 rich [green]을 사용함.
      print(f"Created [green]\"{filename}\"[/green]")
  except FileExistsError:
    err_console.print(f"[green]\"{filename}\"[/green] is already exists.")
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

if __name__ == "__main__":
  app()
