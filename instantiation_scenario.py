import sys
from owlready2 import *
import types

# For example, python instantiation_scenario.py data/SOMA_and_OCRA_refined.owl SOMA_and_OCRA_refined_instantiated.owl

def main():
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <input_ontology.owl> <output_instantiated.owl>")
        sys.exit(1)

    ont_path = sys.argv[1]
    if not ont_path.startswith("file://"):
        ont_path = f"file://{ont_path}"

    output_path = sys.argv[2]

    onto = get_ontology(ont_path).load()
    ontology_ns = types.SimpleNamespace()

    def apply_reasoner(message=""):
        print("\n" + "-"*40)
        print(f"Running reasoner... {message}")
        sync_reasoner()
        print("Reasoner applied.")
        print("-"*40 + "\n")

    with onto:
        for cls in onto.classes():
            setattr(ontology_ns, cls.name, cls)

        Agent_Nurse = ontology_ns.Agent("Agent_Nurse")
        Agent_Shadow = ontology_ns.Agent("Agent_Shadow")
        PhysicalPlace_Hospital = ontology_ns.PhysicalPlace("PhysicalPlace_Hospital")
        PhysicalObject_Medicine = ontology_ns.PhysicalObject("PhysicalObject_Medicine")
        Goal_DeliveryAssistance = ontology_ns.Goal("Goal_DeliveryAssistance")
        Plan_DeliverMedicine = ontology_ns.Plan("Plan_DeliverMedicine")
        Transporting_TransportMedicine = ontology_ns.Transporting("Transporting_TransportMedicine")
        Collaboration_Collaborate = ontology_ns.Collaboration("Collaboration_Collaborate")

        Plan_DeliverMedicine.isPlanFor.append(Transporting_TransportMedicine)
        Plan_DeliverMedicine.hasComponent.append(Goal_DeliveryAssistance)
        Agent_Shadow.hasGoal.append(Goal_DeliveryAssistance)
        Agent_Shadow.hasPlan.append(Plan_DeliverMedicine)
        Agent_Shadow.hasLocation.append(PhysicalPlace_Hospital)
        Agent_Nurse.hasGoal.append(Goal_DeliveryAssistance)
        Agent_Nurse.hasPlan.append(Plan_DeliverMedicine)
        Agent_Nurse.hasLocation.append(PhysicalPlace_Hospital)
        PhysicalObject_Medicine.hasLocation.append(Agent_Shadow)
        Collaboration_Collaborate.executesPlan.append(Plan_DeliverMedicine)

        apply_reasoner("Instantiation created")

    onto.save(output_path, format="rdfxml")

if __name__ == "__main__":
    main()
