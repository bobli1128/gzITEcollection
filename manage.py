# -*- coding:UTF-8 -*-
import os

COV = None
if os.environ.get('FLASKY_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from app import create_app, db
from app.models import User, Role, Post, Comment, Permission, Follow
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


@manager.command
def test(coverage=False):
    """Run the unit test"""
    if coverage and not os.environ.get('FLASKY_COVERAGE'):
        import sys
        os.environ['FALSKY_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable]+sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        COV.erase()


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Comment=Comment,
                Permission=Permission, Follow=Follow)


# print(make_shell_context())

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
