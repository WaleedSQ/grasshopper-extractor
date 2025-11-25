"""
Grasshopper data tree representation.
A data tree is a mapping from path tuples to lists of items.
Path tuples represent GH paths like {0;0} as (0, 0).
"""

from typing import Dict, List, Any, Tuple, Union


class DataTree:
    """Represents a Grasshopper data tree."""
    
    def __init__(self, data: Union[Dict[Tuple[int, ...], List[Any]], List[Any], Any] = None):
        """
        Initialize a data tree.
        
        Args:
            data: Can be:
                - Dict[Tuple[int, ...], List[Any]]: path -> items mapping
                - List[Any]: single branch at path (0,)
                - Any: single item at path (0,)
        """
        if data is None:
            self._tree: Dict[Tuple[int, ...], List[Any]] = {}
        elif isinstance(data, dict):
            # Assume it's already a tree structure
            self._tree = {k: (v if isinstance(v, list) else [v]) for k, v in data.items()}
        elif isinstance(data, list):
            # Single branch at path (0,)
            self._tree = {(0,): data}
        else:
            # Single item at path (0,)
            self._tree = {(0,): [data]}
    
    def get_branch(self, path: Tuple[int, ...]) -> List[Any]:
        """Get items at a specific path."""
        return self._tree.get(path, [])
    
    def set_branch(self, path: Tuple[int, ...], items: List[Any]):
        """Set items at a specific path."""
        self._tree[path] = items if isinstance(items, list) else [items]
    
    def paths(self):
        """Get all paths in the tree."""
        return list(self._tree.keys())
    
    def items(self):
        """Get all (path, items) pairs."""
        return self._tree.items()
    
    def flatten(self) -> List[Any]:
        """Flatten tree to a single list (all items from all branches)."""
        result = []
        for items in self._tree.values():
            result.extend(items)
        return result
    
    def to_list(self) -> Union[List[Any], Any]:
        """
        Convert to simple list/item for backward compatibility.
        If single branch at (0,), return the list.
        If single item at (0,), return the item.
        Otherwise return nested list structure.
        """
        if len(self._tree) == 1 and (0,) in self._tree:
            items = self._tree[(0,)]
            if len(items) == 1:
                return items[0]
            return items
        
        # Multiple branches - return nested structure
        # Sort paths to ensure consistent ordering
        sorted_paths = sorted(self._tree.keys())
        if all(len(p) == 1 for p in sorted_paths):
            # All paths are single-level, return list of branches
            return [self._tree[p] for p in sorted_paths]
        else:
            # Multi-level paths - return nested structure
            result = []
            for path in sorted_paths:
                items = self._tree[path]
                if len(path) == 1:
                    result.append(items)
                else:
                    # Build nested structure
                    current = result
                    for i, level in enumerate(path[:-1]):
                        while len(current) <= level:
                            current.append([])
                        if not isinstance(current[level], list):
                            current[level] = []
                        current = current[level]
                    current.append(items)
            return result
    
    @staticmethod
    def from_list(data: Union[List[Any], Any]) -> 'DataTree':
        """Create a tree from a list or single item."""
        if isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], list):
                # Nested list - treat as multiple branches
                tree = DataTree()
                for i, branch in enumerate(data):
                    tree.set_branch((i,), branch if isinstance(branch, list) else [branch])
                num_branches = len(tree.paths())
                print(f"  DEBUG [TREE-CONV] DataTree.from_list(): nested list, {len(data)} outer items -> {num_branches} branches")
                return tree
            else:
                # List of items - each item becomes its own branch (GH semantics)
                tree = DataTree()
                for i, item in enumerate(data):
                    tree.set_branch((i,), [item])
                num_branches = len(tree.paths())
                num_items = len(data)
                print(f"  DEBUG [TREE-CONV] DataTree.from_list(): flat list, {num_items} items -> {num_branches} branches")
                if num_items > 1 and num_branches == 1:
                    print(f"  DEBUG [TREE-CONV] DataTree.from_list(): ERROR - {num_items} items created only 1 branch!")
                return tree
        else:
            # Single item
            result = DataTree({(0,): [data]})
            print(f"  DEBUG [TREE-CONV] DataTree.from_list(): single item -> 1 branch")
            return result
    
    def __repr__(self):
        return f"DataTree({self._tree})"


def is_tree(data: Any) -> bool:
    """Check if data is a DataTree."""
    return isinstance(data, DataTree)


def to_tree(data: Any) -> DataTree:
    """Convert data to a DataTree if it isn't already."""
    if isinstance(data, DataTree):
        return data
    
    # Debug: log conversion details
    input_type = type(data).__name__
    if isinstance(data, list):
        num_items = len(data)
        result = DataTree.from_list(data)
        num_branches = len(result.paths())
        print(f"  DEBUG [TREE-CONV] to_tree(): input type={input_type}, num_items={num_items}, result_branches={num_branches}")
        if num_items > 1 and num_branches == 1:
            print(f"  DEBUG [TREE-CONV] to_tree(): WARNING - {num_items} items converted to 1 branch (should be {num_items} branches)")
    else:
        result = DataTree.from_list(data)
        num_branches = len(result.paths())
        print(f"  DEBUG [TREE-CONV] to_tree(): input type={input_type}, result_branches={num_branches}")
    
    return result


def from_tree(data: Any) -> Union[List[Any], Any]:
    """Convert DataTree to list/item for backward compatibility."""
    if isinstance(data, DataTree):
        return data.to_list()
    return data

