import click

@click.group()
def cli():
    """기본 CLI 명령 그룹"""
    pass

@cli.command(name="write")
@click.argument('lba')
@click.argument('data')
def write(lba, data):
    """wirte"""
    pass

@cli.command(name="read")
@click.argument('lba')
def read(lba):
    pass

@cli.command(name="fullwrite")
def fullwrite():
    pass

@cli.command(name="fullread")
def fullread():
    pass

@cli.command(name="help")
def help():
    click.echo("help me")

@cli.command()
def shell():
    """무한 루프 쉘 모드"""
    click.echo("📥 Shell 모드 진입. 'exit' 입력 시 종료됩니다.")
    while True:
        try:
            user_input = input("Shell > ").strip()
            if user_input in ('exit', 'quit'):
                click.echo("👋 종료합니다.")
                break
            elif user_input.startswith("write"):
                # 인자 check 및 에러 처리 필요
                write.callback(3, 0xAAAABBBB)
            elif user_input.startswith("read"):
                # 인자 check 및 에러 처리 필요
                read.callback(3)
            elif user_input == "fullwrite":
                fullwrite.callback()
            elif user_input == "fullread":
                fullread.callback()
            elif user_input == "help":
                help.callback()
                click.echo("help")
            else:
                click.echo("❓ 알 수 없는 명령입니다.")
        except (KeyboardInterrupt, EOFError):
            click.echo("\n👋 종료합니다.")
            break


if __name__ == '__main__':
        cli()