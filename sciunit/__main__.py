import sys
import os
import argparse
import configparser
import io

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="create, check, or run")
    parser.add_argument("--directory", "-dir", default=os.getcwd(), 
                        help="path to directory with a .sciunit file")
    parser.add_argument("--stop", "-s", default=True, 
                        help="stop and raise errors, halting the program")
    args = parser.parse_args()
    #args.directory = os.getcwd() if args.directory is None else args.directory
    file_path = os.path.join(args.directory,'.sciunit')
    if args.action == 'create':
        create(file_path)
    elif args.action == 'check':
        config = parse(file_path, show=True)
        print("\nNo configuration errors reported.")
    elif args.action == 'run':
        config = parse(file_path)
        run(config, path=args.directory, stop_on_error=args.stop)
    else:
        raise NameError('No such action %s' % args.action)


def create(file_path):
    """Create a default .sciunit config file if one does not already exist"""
    if os.path.exists(file_path):
        raise IOError("There is already a configuration file at %s" % file_path)
    with open(file_path,'w') as f:
        config = configparser.ConfigParser()
        config.add_section('misc')
        config.set('misc', 'config-version', '1.0')
        config.add_section('root')
        config.set('root', 'path', '.')
        config.add_section('models')
        config.set('models', 'module', 'models')
        config.add_section('tests')
        config.set('tests', 'module', 'tests')
        config.add_section('suites')
        config.set('suites', 'module', 'suites')
        config.write(f)


def parse(file_path=None, show=False):
    """Parse a .sciunit config file"""
    if file_path is None:
        path = os.path.join(os.getcwd(),'.sciunit')
    if not os.path.exists(file_path):
        raise IOError('No .sciunit file was found at %s' % file_path)

    # Load the configuration file
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read(file_path)

    # List all contents
    for section in config.sections():
        if show:
            print(section)
        for options in config.options(section):
            if show:
                print("\t%s: %s" % (options,config.get(section, options)))
    return config


def prep(config=None, path=None):
    if config is None:
        config = parse()
    if path is None:
        path = os.getcwd()
    root = config.get('root','path')
    root = os.path.join(path,root)
    if sys.path[0] != root:
        sys.path.insert(0,root)


def run(config, path=None, stop_on_error=True):
    """Run sciunit tests for the given configuration"""
    
    if path is None:
        path = os.getcwd()
    prep(config, path=path)

    models = __import__('models')
    tests = __import__('tests')
    suites = __import__('suites')

    for x in ['models','tests','suites']:
        module = __import__(x)
        assert hasattr(module,x), "'%s' module requires attribute '%s'" % (x,x)     

    for test in tests.tests:
        score_array = test.judge(models.models, stop_on_error=stop_on_error)
        print('Test %s:\n%s' % (test,score_array))

    for suite in suites.suites:
        score_matrix = suite.judge(models.models, stop_on_error=stop_on_error)
        print('Suite %s:\n%s' % (suite,score_matrix))

if __name__ == '__main__':
    main()

