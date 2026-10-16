from application.bootstrap import create_mediator
from infrastructure.persistence.json import JsonUnitOfWork
from presentation.kivy_ui.app import TasklyApp


def main():
    mediator = create_mediator(JsonUnitOfWork())
    TasklyApp(mediator).run()


if __name__ == "__main__":
    main()
