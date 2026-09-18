'''
Tree view: display bookmarks grouped by label category (with nested
parent categories) or by URL domain.
'''

from src import labels as labels_module
from src.search import domain_of

UNCATEGORIZED = "Uncategorized"
NO_LABEL = "No label"

def group_by_category(bookmarks, config):
    """
    Group bookmarks into a tree of root category -> category -> label.

    Args:
        bookmarks : list of existing bookmarks
        config : configuration dict, used to resolve each label's
            category and each category's root ancestor (see
            labels.category_of and labels.root_category_of)

    Returns:
        Nested dict {root_category: {category: {label: [bookmarks]}}}.
        A label with no configured category is grouped under
        "Uncategorized" / "Uncategorized" / label. A bookmark with no
        labels is grouped under "Uncategorized" / "Uncategorized" /
        "No label".

    Effects:
        None (pure function).
    """
    tree = {}

    def add(root, category, label, bookmark):
        tree.setdefault(root, {}).setdefault(category, {}).setdefault(label, []).append(bookmark)

    for bookmark in bookmarks:
        if not bookmark[7]:
            add(UNCATEGORIZED, UNCATEGORIZED, NO_LABEL, bookmark)
            continue
        for label in bookmark[7]:
            category = labels_module.category_of(label, config)
            if category is None:
                add(UNCATEGORIZED, UNCATEGORIZED, label, bookmark)
            else:
                root = labels_module.root_category_of(category, config)
                add(root, category, label, bookmark)

    return tree

def group_by_domain(bookmarks):
    """
    Group bookmarks by their URL domain.

    Args:
        bookmarks : list of existing bookmarks

    Returns:
        Dict {domain: [bookmarks]}

    Effects:
        None (pure function).
    """
    tree = {}
    for bookmark in bookmarks:
        tree.setdefault(domain_of(bookmark), []).append(bookmark)
    return tree

def print_tree(bookmarks, config, by="category"):
    """
    Print the bookmarks grouped in a tree view.

    Args:
        bookmarks : list of existing bookmarks
        config : configuration dict, used when by == "category"
        by : "category" (default) or "domain"

    Effects:
        Prints the tree to stdout.
    """
    if by == "domain":
        for domain, domain_bookmarks in sorted(group_by_domain(bookmarks).items()):
            print(domain)
            for bookmark in sorted(domain_bookmarks, key=lambda b: b[0]):
                print(f"  [{bookmark[0]}] {bookmark[1]}")
        return

    tree = group_by_category(bookmarks, config)
    for root, categories in sorted(tree.items()):
        print(root)
        for category, category_labels in sorted(categories.items()):
            print(f"  {category}")
            for label, label_bookmarks in sorted(category_labels.items()):
                print(f"    {label}")
                for bookmark in sorted(label_bookmarks, key=lambda b: b[0]):
                    print(f"      [{bookmark[0]}] {bookmark[1]}")
