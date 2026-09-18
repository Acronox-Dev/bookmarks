'''
Label helpers: automatic classification of a bookmark's labels from its
URL (rules-driven), and category lookups for labels, including nested
categories (used by the tree view and statistics).
'''

def classify(url, labels, config):
    """
    Add any labels the configured URL rules assign to a URL, on top of
    the labels already given by the user.

    Args:
        url : the bookmark's URL
        labels : tuple of labels already associated with the bookmark
        config : configuration dict, using config['url_label_rules'], a
            dict of {url_substring: label}

    Returns:
        labels, extended with every rule's label whose url_substring is
        contained in url and that is not already present, in rule order

    Effects:
        None (pure function).
    """
    auto_labels = tuple(
        label for url_substring, label in config["url_label_rules"].items()
        if url_substring in url and label not in labels
    )
    return labels + auto_labels

def category_of(label, config):
    """
    Look up the category a label belongs to.

    Args:
        label : the label to look up
        config : configuration dict, using config['label_categories'], a
            dict of {label: category}

    Returns:
        The label's category, or None if the label has no category

    Effects:
        None (pure function).
    """
    return config["label_categories"].get(label)

def root_category_of(category, config):
    """
    Walk up the configured category hierarchy to find a category's
    top-level ancestor.

    Args:
        category : the category to start from
        config : configuration dict, using config['category_parents'], a
            dict of {category: parent_category}

    Returns:
        category itself if it has no parent (or is its own parent),
        otherwise the root ancestor found by following category_parents

    Effects:
        None (pure function).
    """
    parent = config["category_parents"].get(category)
    if parent is None or parent == category:
        return category
    return root_category_of(parent, config)
