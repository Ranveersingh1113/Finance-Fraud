# Knowledge Graphs Directory

This directory stores generated knowledge graphs.

## Files (Not in Git)
- `.gpickle` files are ignored (binary graph storage)
- `.json` files are ignored (large graph exports)
- Graphs are generated from data, not source code

## Generated Files
- `sebi_knowledge_graph.gpickle` - SEBI entity/violation graph
- `sebi_knowledge_graph.json` - JSON export
- `sebi_graph_visualization.json` - Visualization data

## Regenerate
Run `python build_sebi_knowledge_graph.py` to rebuild graphs.

