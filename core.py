def add(bookmarks, details) :
    """
    Add a new bookmark into the list of current bookmarks  
                                                   
    Arguments :                                            
        bookmarks : list of bookmarks                        
        details : Array values to describe the bookmark 
                                                     
    Returns:  
        The new bookmark                               
    """
    bookmark = f"1, {details}\n"
    
    if bookmarks :
        new_id = max(map(lambda b: int(b.split(",")[0]), bookmarks)) + 1
        bookmark = f"{new_id}, {details}\n"
        
    return bookmark

def modify(bookmarks, id, new_details):
    """
    Modify an existing bookmark with new details.

    Args: 
        bookmarks : list of existing bookmarks
        id : id of the bookmark to modify
        new_details : new details to update the bookmark with
    
    Returns:
        Updated list of bookmarks with the modified bookmark
    """
    updated_bookmarks = list(filter(lambda b: str(id) + new_details if b.split(",")[0] != id else b, bookmarks))
    return updated_bookmarks


def rm(bookmarks, id):
    """
    Remove a bookmark from the list of bookmarks.

    Args:
        bookmarks : list of existing bookmarks
        id : id of the bookmark to modify

    Returns:
        Updated list of bookmarks without the removed bookmark
    """
    updated_bookmarks = list(filter(lambda b: b.split(",")[0] != id, bookmarks))
    return updated_bookmarks


def show(bookmarks) :
    """
    Display the bookmarks in a formatted table.

    Args:
        bookmarks : list of existing bookmarks
    """
    sorted_bookmarks = ["id,title,url,notes"] + sorted(bookmarks, key =lambda x: int(x.split(",")[0]))
    lengths = [map(len, str(b).split(",")) for b in sorted_bookmarks]
    max_lengths = list(map(max, *lengths))

    border = "+" + "+".join("-" * (length + 2) for length in max_lengths) + "+"

    def recursive_print(i) :
        if i >= len(sorted_bookmarks) :
            return

        values = sorted_bookmarks[i].split(",")
        strings = [v.strip() for v in values]

        for j in range(len(strings)) :
            print("| ", end ="")
            print(strings[j], end=" " * (max_lengths[j] - len(strings[j]) + 1))

        print("|")
        print(border)
        recursive_print(i + 1)

    print(border)
    recursive_print(0)