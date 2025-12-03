from .simple_types import Resource, GridPosition
from collections import Counter
from .interfaces import InterfaceGrid, ProcessActionInterface, InterfaceCard

class ProcessAction(ProcessActionInterface):
    def activateCard(self, card: InterfaceCard, grid: InterfaceGrid, 
                     inputs: list[tuple[Resource, GridPosition]], 
                     outputs: list[tuple[Resource, GridPosition]], 
                     pollution: list[GridPosition]) -> bool:
        """Checks whether the action is valid, and if so performs it."""

        if not card.isActive():
            return False

        #check pollution for each position
        counted_pollution = Counter(pollution)
        for position, count in counted_pollution.items():
            pollution_card = grid.getCard(position)
            if pollution_card is None:
                return False
            if not pollution_card.canPlacePollution(count):
                return False
        #check inputs for each position
        inputs_grouped: dict[GridPosition, list[Resource]] = {}
        for resource, position in inputs:
            inputs_grouped.setdefault(position, []).append(resource)

        for position, resources in inputs_grouped.items():
            input_card = grid.getCard(position)
            if input_card is None:
                return False
            if not input_card.canGetResources(resources):
                return False
        #check outputs for each position
        outputs_grouped: dict[GridPosition, list[Resource]] = {}
        outputs_resources: list[Resource] = []
        for resource, position in outputs:
            outputs_grouped.setdefault(position, []).append(resource)
        if len(outputs_grouped) > 1:
            return False
        elif len(outputs_grouped) == 1:
            output_card_position = next(iter(outputs_grouped))
            outputs_resources = outputs_grouped[output_card_position]
            output_card = grid.getCard(output_card_position)
            if output_card is None:
                return False
            if output_card.state() != card.state() or not card.canPutResources(outputs_resources):
                return False

        inputs_resources: list[Resource] = [input[0] for input in inputs]

        if card.check(inputs_resources, outputs_resources, len(pollution)) or card.checkLower(inputs_resources, outputs_resources, len(pollution)):
            #perform action
            for position, resources in inputs_grouped.items():
                input_card = grid.getCard(position)
                if input_card is None:
                    return False
                input_card.getResources(resources)
            for position, resources in outputs_grouped.items():
                output_card = grid.getCard(position)
                if output_card is None:
                    return False
                output_card.putResources(resources)

            for position, count in counted_pollution.items():
                pollution_card = grid.getCard(position)
                if pollution_card is None:
                    return False
                pollution_card.placePollution(count)
            return True

        return False
