from rdflib import Graph, Namespace, RDF, RDFS, OWL, BNode, URIRef, Literal

def collect_bnode_triples(bnode, graph, collected, visited_set):
    if bnode in visited_set:
        return
    visited_set.add(bnode)
    for p, o in graph.predicate_objects(bnode):
        collected.add((bnode, p, o))
        if isinstance(o, BNode):
            collect_bnode_triples(o, graph, collected, visited_set)
        if p in [RDF.first, RDF.rest]:
            if isinstance(o, BNode):
                collect_bnode_triples(o, graph, collected, visited_set)
            elif isinstance(o, URIRef):
                if o not in classes_to_add:
                    classes_to_add.add(o)
                    classes_to_process.append(o)


g = Graph()
g.parse("data/SOMA_and_OCRA.owl", format="xml")

refined = Graph()
for prefix, ns in g.namespaces():
    refined.bind(prefix, ns)

clases_base_nombres = {
    "Agent", "Collaboration", "PhysicalPlace", 
    "PhysicalObject", "Transporting", "Goal"
}
palabras_clave_causales = {
    "cause", "caus", "depend", "result", 
    "precondition", "answeredby"
}

def get_local_name(uri_str):
    return uri_str.split('#')[-1].split('/')[-1]

all_visited_bnodes = set()

base_class_uris = set()
for s in g.subjects(RDF.type, OWL.Class):
    if get_local_name(str(s)) in clases_base_nombres:
        base_class_uris.add(s)
for s in g.subjects(RDF.type, RDFS.Class):
    if get_local_name(str(s)) in clases_base_nombres:
        base_class_uris.add(s)

causal_prop_uris = set()
for p in g.subjects(RDF.type, OWL.ObjectProperty):
    name = get_local_name(str(p)).lower()
    if any(keyword in name for keyword in palabras_clave_causales):
        causal_prop_uris.add(p)

dub_classes = list(base_class_uris)
classes_to_process = list(base_class_uris)
classes_to_add = set(base_class_uris)
subclass_triples = set()
restriction_triples = set()
property_uris = set()
bnode_triples = set()

while classes_to_process:
    cls = classes_to_process.pop()
    for o in g.objects(cls, RDFS.subClassOf):
        if isinstance(o, URIRef):
            subclass_triples.add((cls, RDFS.subClassOf, o))
            if o not in classes_to_add:
                classes_to_add.add(o)
                classes_to_process.append(o)
        elif isinstance(o, BNode):
            restriction_triples.add((cls, RDFS.subClassOf, o))
            collect_bnode_triples(o, g, bnode_triples, all_visited_bnodes)
            for p, o2 in g.predicate_objects(o):
                if p in [OWL.onProperty, OWL.onDataRange, OWL.onClass] and isinstance(o2, URIRef):
                    property_uris.add(o2)
                if p in [OWL.allValuesFrom, OWL.someValuesFrom, OWL.onClass]:
                    if isinstance(o2, URIRef):
                        if o2 not in classes_to_add:
                            classes_to_add.add(o2)
                            classes_to_process.append(o2)
                    elif isinstance(o2, BNode):
                        collect_bnode_triples(o2, g, bnode_triples, all_visited_bnodes)
                if p in [OWL.intersectionOf, OWL.unionOf] and isinstance(o2, BNode):
                    collect_bnode_triples(o2, g, bnode_triples, all_visited_bnodes)

causal_triples = set()
for cls in list(classes_to_add):
    for prop in causal_prop_uris:
        for obj in g.objects(cls, prop):
            if isinstance(obj, URIRef) and ((obj, RDF.type, OWL.Class) in g or (obj, RDF.type, RDFS.Class) in g):
                classes_to_add.add(obj)
                causal_triples.add((cls, prop, obj))
        for subj in g.subjects(prop, cls):
            if isinstance(subj, URIRef) and ((subj, RDF.type, OWL.Class) in g or (subj, RDF.type, RDFS.Class) in g):
                classes_to_add.add(subj)
                causal_triples.add((subj, prop, cls))

for cls in classes_to_add:
    refined.add((cls, RDF.type, OWL.Class))
for triple in subclass_triples:
    refined.add(triple)
for triple in restriction_triples:
    refined.add(triple)
for triple in causal_triples:
    refined.add(triple)

for s, p, o in bnode_triples:
    if p == OWL.onProperty and isinstance(o, URIRef):
        property_uris.add(o)

property_uris |= causal_prop_uris
for prop in property_uris:
    for p, o in g.predicate_objects(prop):
        refined.add((prop, p, o))
        if isinstance(o, BNode):
            collect_bnode_triples(o, g, bnode_triples, all_visited_bnodes)
    for s, p in g.subject_predicates(prop):
        refined.add((s, p, prop))
        if isinstance(s, BNode):
            collect_bnode_triples(s, g, bnode_triples, all_visited_bnodes)
    for d in g.objects(prop, RDFS.domain):
        refined.add((prop, RDFS.domain, d))
    for r in g.objects(prop, RDFS.range):
        refined.add((prop, RDFS.range, r))


for s, p, o in bnode_triples:
    if isinstance(o, Literal) and not o.datatype:
        continue
    refined.add((s, p, o))


refined.serialize("data/SOMA_and_OCRA_refined.owl", format="xml")

print("\nRefined Ontology created")
print("=" * 60)
print(f"Number of Classes: {len(classes_to_add)}")
print(f"Causal properties: {len(causal_prop_uris)}")
print("=" * 60)