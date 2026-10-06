"""``gov context`` command module (DEC-317)."""

CLASS = "read"
ACT_PATHS = ()


def add_arguments(parser):
    parser.add_argument("ticket")
    parser.add_argument("--brief", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--budget", type=int, default=None)


def run(root, args, config):
    from gov.context import context
    return context(root, args.ticket, brief=args.brief, budget=args.budget,
                   dry_run=getattr(args, "dry_run", False))
