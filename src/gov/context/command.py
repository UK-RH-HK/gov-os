"""``gov context`` command module (DEC-317); ``--in-force`` gives the digest of the decisions in force (W2-55)."""

CLASS = "read"
ACT_PATHS = ()


def add_arguments(parser):
    which = parser.add_mutually_exclusive_group(required=True)  # a ticket, or --in-force: one of the two
    which.add_argument("ticket", nargs="?")
    which.add_argument("--in-force", action="store_true",
                       help="the digest of the register's decisions in force, generated from HEAD")
    parser.add_argument("--brief", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--budget", type=int, default=None)


def run(root, args, config):
    if getattr(args, "in_force", False):
        from gov.decisions.register import in_force
        return in_force(root)
    from gov.context import context
    # W2-13 S5 (DEC-1065 (2)): a --role given adds its role-paths filter to the supplementary block beside GOV_ROLE's
    return context(root, args.ticket, brief=args.brief, budget=args.budget,
                   dry_run=getattr(args, "dry_run", False), role=getattr(args, "role", None))
