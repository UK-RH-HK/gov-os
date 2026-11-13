p = "src/gov/resources/command.py"
s = open(p).read()
s = s.replace('''ACT_PATHS = ()  # everything it writes is under ~/.gov-os/machine/, outside the project''',
'''ACT_PATHS = (".gov-runtime/dispatch/inbox/**",)  # else under ~/.gov-os/machine/; --backstop's one inbox item is here''')
s = s.replace('''def add_arguments(parser) -> None:''', '''def _group(text: str) -> int:
    """A process group id: a decimal integer above 1 (S4); anything else is argparse's usage error naming it."""
    import argparse

    if not text.isascii() or not text.isdigit() or int(text) <= 1:
        raise argparse.ArgumentTypeError(f"not a process group id (a decimal integer above 1): {text!r}")
    return int(text)


def add_arguments(parser) -> None:''')
s = s.replace('''    parser.add_argument("--gpu-need-mib", metavar''', '''    mode.add_argument("--backstop", metavar="<pgid>", nargs="+", type=_group,
                      help="watch these process groups of a GPU job and pause them on a GPU trip (limit, spill, embedder)")
    parser.add_argument("--gpu-need-mib", metavar''', 1)
s = s.replace('''    if args.register is not None:
        from gov.resources.registry import folder, register''', '''    if args.backstop:
        from gov.resources.backstop import watch
        return watch(args.backstop, root)
    if args.register is not None:
        from gov.resources.registry import folder, register''', 1)
s = s.replace('''args.trip_wire, args.slot))''', '''args.trip_wire, args.slot, args.backstop))''')
open(p, "w").write(s)

t = "tests/unit/resources/test_w2_157_backstop.py"
s = open(t).read()
s = s.replace('''    done = subprocess.run([sys.executable, "-m", "gov", "resources", *argv, "--root", str(rig.root)],''',
'''    done = subprocess.run([sys.executable, "-c", "import sys; from gov.cli.main import main; sys.exit(main(sys.argv[1:]))",
                           "resources", *argv, "--root", str(rig.root)],''')
open(t, "w").write(s)
