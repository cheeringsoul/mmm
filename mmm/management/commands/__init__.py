import os
from jinja2 import Template


def create_project(name, location=None):
    tpl = """
def main():
    ...


if __name__ == '__main__':
    main()

    """
    if location is None:
        location = os.getcwd()
    os.mkdir(os.path.join(location, name))
    rv = Template(tpl).render(project_name_upper=name.upper(), project_name=name)
    f = os.path.join(location, name, 'manage.py')
    print(f)
    with open(f, 'w') as f:
        f.write(rv)


