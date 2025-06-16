from owlready2 import *
from rdflib import Graph

onto = get_ontology("file://data/SOMA_and_OCRA_refined_instantiated.owl").load()
g = default_world.as_rdflib_graph()

g.bind("dul", "http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#")
g.bind("ocra", "http://www.iri.upc.edu/groups/perception/OCRA/ont/ocra.owl#")
g.bind("soma", "http://www.ease-crc.org/ont/SOMA.owl#")

def run_sparql(name, sparql):
    print(name)
    results = list(g.query(sparql))
    if not results:
        print("(no hay resultados)")
    else:
        for row in results:
            print(tuple(row))

cq1 = """
PREFIX dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
SELECT ?goal WHERE {
  ?goal a dul:Goal .
}
"""
print("\n")
print("-" * 40)
run_sparql("CQ1 - What is the goal of the operation?", cq1)

cq2 = """
PREFIX dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
SELECT ?plan WHERE {
  ?goal a dul:Goal .
  ?plan a dul:Plan ;
        dul:hasComponent ?goal .
}
"""
print("\n")
print("-" * 40)
run_sparql("CQ2 - What is the plan to achieve the goal", cq2)

cq3 = """
PREFIX dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
PREFIX soma: <http://www.ease-crc.org/ont/SOMA.owl#>
SELECT ?task WHERE {
  ?plan a dul:Plan ;
        soma:isPlanFor ?task .
  ?task a soma:Transporting .
}
"""
print("\n")
print("-" * 40)
run_sparql("CQ3 - What task is to be performed according to plan?", cq3)

cq4 = """
PREFIX dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
SELECT ?agent ?loc WHERE {
  ?agent a dul:Agent ;
         dul:hasLocation ?loc .
}
"""
print("\n")
print("-" * 40)
run_sparql("CQ4 - Which agents are present, and where are they located", cq4)

cq5 = """
PREFIX ocra: <http://www.iri.upc.edu/groups/perception/OCRA/ont/ocra.owl#>
PREFIX dul:  <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
SELECT ?collab ?agent WHERE {
  ?collab a ocra:Collaboration ;
          ocra:executesPlan ?plan .
  ?agent a dul:Agent ;
         ocra:hasPlan ?plan .
}
"""
print("\n")
print("-" * 40)
run_sparql("CQ5 - What collaboration is taking place, and who is collaborating", cq5)

cq6 = """
PREFIX dul: <http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#>
SELECT ?object WHERE {
  ?object a dul:PhysicalObject ;
          dul:hasLocation ?agent .
}
"""
print("\n")
print("-" * 40)
run_sparql("CQ6 - What objects does the Robot have", cq6)
