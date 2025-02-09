import random
from .utility import *
from .dataparser import RandomizerData
from .difficultyanalysis import compute_average_goal_level

#START_LOCATION = 'FOREST_START'

class Analyzer(object):
    # -- Results --
    #
    # success: bool (True if verification success, False otherwise)
    # error_message: string (error message if success == False)
    #
    # -- The following attributes will only be assigned if success == True. --
    # reachable
    # unreachable
    # levels
    # hard_to_reach_items

    def __init__(self, data: RandomizerData, settings, allocation, goals=None, visualize=False):
        self.data = data
        self.settings = settings
        self.allocation = allocation
        self.visualize = visualize
        self.goals = goals

        self.error_message = ''
        self.success = self.run_verifier()

    def run_verifier(self):
        starting_variables = self.data.generate_variables()
        result, backward_exitable = self.verify_warps_reachable(starting_variables)
        if not result:
            self.error_message = 'Not all warps reachable.'
            return False
        reachable, unreachable, levels, _ = self.verify_reachable_items(starting_variables, backward_exitable)

        # ensure all must_be_reachable items are reachable.
        if not set(self.data.must_be_reachable).issubset(reachable):
            self.error_message = 'Not all must_be_reachable items are reachable.'
            return False

        if self.goals != None and not set(self.goals).issubset(reachable):
            self.error_message = 'Not all goals are reachable.'
            return False

        error = self.process_verification_results(reachable, unreachable, levels)
        if error:
            self.error_message = error
            return False

        if not self.verify_chain_length_requirement(levels):
            self.error_message = 'Below minimum chain length.'
            return False

        return True

    def verify_chain_length_requirement(self, levels):
        if self.goals != None and self.settings.min_chain_length > 0:
            if compute_average_goal_level(set(self.goals), levels) < self.settings.min_chain_length:
                return False
        return True

    def process_verification_results(self, reachable, unreachable, levels):
        #all_levels = [x for x in levels for x in x]
        #print_ln(set(reachable) - set(all_levels))
        #print_ln(len(all_levels), len(set(all_levels)), len(reachable), len(unreachable))
        #print_ln(set(all_levels) - set(reachable))

        allocated_items_set = set(self.data.items_to_allocate)
        nHardToReach = self.data.nHardToReach
        minHardToReachPoolSize = nHardToReach * 5

        hard_to_reach_all = []
        nonempty_levels = 0
        for level in reversed(levels):
            # sort to make it deterministic
            additional_hard_to_reach_items = sorted(allocated_items_set.intersection(level))
            if len(additional_hard_to_reach_items) > 0:
                nonempty_levels += 1
            hard_to_reach_all += additional_hard_to_reach_items
            if len(hard_to_reach_all) >= minHardToReachPoolSize and nonempty_levels >= 2:
                break

        if len(hard_to_reach_all) < nHardToReach:
            return 'Not enough reachable items (%d) for hard to reach (%d)...?' % (len(hard_to_reach_all), nHardToReach)

        if self.settings.egg_goals:
            hard_to_reach_egg = [item for item in hard_to_reach_all if is_egg(item)]

            # hard-to-reach priority
            # egg > potion > other
            nHardToReachEgg = len(hard_to_reach_egg)
            if nHardToReachEgg >= nHardToReach:
                self.hard_to_reach_items = random.sample(hard_to_reach_egg, nHardToReach)
            else:
                self.hard_to_reach_items = random.sample(hard_to_reach_egg, nHardToReachEgg)
                hard_to_reach_potion = [item for item in hard_to_reach_all if is_potion(item)]
                nHardToReachPotion = len(hard_to_reach_potion)
                if (nHardToReachEgg + nHardToReachPotion >= nHardToReach):
                    self.hard_to_reach_items += random.sample(hard_to_reach_potion, nHardToReach - nHardToReachEgg)
                else:
                    self.hard_to_reach_items += random.sample(hard_to_reach_potion, nHardToReachPotion)
                    hard_to_reach_other = [item for item in hard_to_reach_all if not is_potion(item) and not is_egg(item)]
                    self.hard_to_reach_items += random.sample(hard_to_reach_other, nHardToReach - nHardToReachEgg - nHardToReachPotion)

        else:
            self.hard_to_reach_items = random.sample(hard_to_reach_all, nHardToReach)
        self.reachable = reachable
        self.unreachable = unreachable
        self.levels = levels

        if self.goals == None:
            self.goals = self.hard_to_reach_items

        return None


    def verify_warps_reachable(self, starting_variables, diff_analysis = False):
        # verify that every major location has an unconstrained path to the goal.
        variables = starting_variables #should make a copy, but we don't modify variables anyway so we optimize this out.
        allocation = self.allocation
        edges = allocation.edges
        data = self.data

        if diff_analysis:
            dfs_stack = [location for location, loc_type in data.locations.items() if loc_type == LOCATION_WARP]
            visited = set(dfs_stack)
            pending_static_edges = []
            dynamic_edges_id = 0
        else:
            dfs_stack = data.initial_pending_stack.copy()
            visited = data.initial_visited_edges.copy()
            pending_static_edges = data.pending_static_edges
            dynamic_edges_id = data.dynamic_edges_id

        while len(dfs_stack) > 0:
            current_dest = dfs_stack.pop()
            for edge_id in allocation.incoming_edges[current_dest]:
                if edge_id < dynamic_edges_id:
                    if pending_static_edges[edge_id]:
                        target_src = edges[edge_id].from_location
                        if target_src in visited: continue
                        visited.add(target_src)
                        dfs_stack.append(target_src)
                else:
                    target_src = edges[edge_id].from_location
                    if target_src in visited: continue
                    if edges[edge_id].satisfied(variables):
                        visited.add(target_src)
                        dfs_stack.append(target_src)

        major_locations = set(location for location, loc_type in data.locations.items() if loc_type == LOCATION_MAJOR)

        return (len(major_locations - visited) == 0, visited)


    def verify_reachable_items(self, starting_variables, backward_exitable):
        if self.visualize:
            from visualizer import Visualization
            vis = Visualization(self.settings)
            vis.load_graph(self.data, self.allocation)

        data = self.data
        allocation = self.allocation

        # Should not be modified:
        edges = allocation.edges
        outgoing_edges = allocation.outgoing_edges
        incoming_edges = allocation.incoming_edges
        locations_set = data.locations_set
        edge_progression = data.edge_progression

        # Persistent variables
        variables = dict(starting_variables)
        untraversable_edges = data.initial_untraversable_edges.copy()
        unreached_pseudo_items = dict(data.pseudo_items)
        unsatisfied_item_conditions = dict(data.alternate_conditions)
        edge_progression_default = edge_progression['DEFAULT'].copy()

        forward_enterable = set((allocation.start_location.location,))
        backward_exitable = set(backward_exitable)
        pending_exit_locations = set()
        locally_exitable_locations = {}

        levels = []

        # Temp Variables that are reset every time
        to_remove = []
        forward_frontier = set((allocation.start_location.location,))
        backward_frontier = data.initial_backward_frontier.copy()
        new_reachable_locations = forward_enterable.intersection(backward_exitable)
        newly_traversable_edges = data.initial_traversable_edges.copy()
        temp_variable_storage = {}
        previous_new_variables = set() # for step 1 updating edges
        new_variables_edges = set()
        edge_progression_default -= newly_traversable_edges

        variables['IS_BACKTRACKING'] = False
        variables['BACKTRACK_DATA'] = untraversable_edges, outgoing_edges, edges
        variables['BACKTRACK_GOALS'] = None, None

        reachable_levels = {allocation.start_location.location : 0}

        #step -1: Mark variables that start True (step 1 checks these)
        previous_new_variables.update(var for var,val in variables.items() if val == True)

        while True:
            current_level_part1 = []
            current_level_part2 = []

            # STEP 0: Mark Pseudo-Items
            has_changes = True
            while has_changes:
                has_changes = False

                # 0 Part A: Handle pseudo-items
                to_remove.clear()
                for target, condition in unreached_pseudo_items.items():
                    if condition(variables):
                        current_level_part1.append(target)
                        to_remove.append(target)
                        variables[target] = True
                        has_changes = True

                for target in to_remove:
                    del unreached_pseudo_items[target]

                # 0 Part B: Handle alternate constraints for items
                to_remove.clear()
                for target, condition in unsatisfied_item_conditions.items():
                    if condition(variables):
                        if not variables[target]:
                            current_level_part1.append(target)
                            variables[target] = True
                            has_changes = True
                        to_remove.append(target)

                for target in to_remove:
                    del unsatisfied_item_conditions[target]
            previous_new_variables.update(current_level_part1)


            # STEP 1: Loop Edge List
            new_variables_edges.clear()
            for var in previous_new_variables:
                if len(edge_progression[var]) > 0:
                    new_variables_edges |= edge_progression[var]
            new_variables_edges &= untraversable_edges
            new_variables_edges |= edge_progression_default
            for edge_id in new_variables_edges:
                edge = edges[edge_id]
                if edge.satisfied(variables):
                    newly_traversable_edges.add(edge_id)
                    if edge.from_location in forward_enterable:
                        forward_frontier.add(edge.from_location)
                    if edge.to_location in backward_exitable:
                        backward_frontier.add(edge.to_location)

            previous_new_variables.clear()
            edge_progression_default -= newly_traversable_edges
            untraversable_edges -= newly_traversable_edges
            newly_traversable_edges.clear()

            # STEP 2: Find Forward Reachable Nodes
            new_forward_enterable = set()
            while len(forward_frontier) > 0:
                for node in forward_frontier:
                    for edge_id in outgoing_edges[node]:
                        if edge_id not in untraversable_edges:
                            target_location = edges[edge_id].to_location
                            if target_location not in forward_enterable:
                                new_forward_enterable.add(target_location)
                                forward_enterable.add(target_location)
                                if target_location in backward_exitable:
                                    new_reachable_locations.add(target_location)
                                else:
                                    pending_exit_locations.add(target_location)
                forward_frontier.clear()
                forward_frontier, new_forward_enterable = new_forward_enterable, forward_frontier


            # STEP 3: Find Exitable Nodes
            new_backward_exitable = set()
            while len(backward_frontier) > 0:
                for node in backward_frontier:
                    for edge_id in incoming_edges[node]:
                        if edge_id not in untraversable_edges:
                            target_location = edges[edge_id].from_location
                            if target_location not in backward_exitable:
                                new_backward_exitable.add(target_location)
                                backward_exitable.add(target_location)

                                if target_location in forward_enterable:
                                    new_reachable_locations.add(target_location)
                                    pending_exit_locations.remove(target_location)
                backward_frontier.clear()
                backward_frontier, new_backward_exitable = new_backward_exitable, backward_frontier


            # STEP 4: Mark New Reachable Locations
            for location in new_reachable_locations:
                if self.visualize:
                    if location not in reachable_levels:
                        reachable_levels[location] = len(levels)//2
                if location in locations_set:
                    if not variables[location]:
                        current_level_part2.append(location)
                        #variables[location] = True
                for item_location in data.item_locations_in_node[location]:
                    item_name = allocation.item_at_item_location[item_location]
                    if item_name == None: continue
                    if not variables[item_name]:
                        current_level_part2.append(item_name)
                        #variables[item_name] = True

            new_reachable_locations.clear()


            # STEP 5: Handle Pending Exit Locations
            for base_location in pending_exit_locations:
                # Temporarily Mark Variables
                variables['IS_BACKTRACKING'] = True
                temp_variable_storage.clear()
                if base_location in locations_set:
                    temp_variable_storage[base_location] = variables[base_location]
                    variables[base_location] = True
                for item_location in data.item_locations_in_node[base_location]:
                    item_name = allocation.item_at_item_location[item_location]
                    if item_name == None: continue
                    temp_variable_storage[item_name] = variables[item_name]
                    variables[item_name] = True

                if base_location not in locally_exitable_locations:
                    locally_exitable_locations[base_location] = set((base_location,))
                locally_exitable = locally_exitable_locations[base_location]

                can_exit = False
                local_backward_frontier = set(locally_exitable)
                new_locally_backward_exitable = set()
                while len(local_backward_frontier) > 0 and not can_exit:
                    for node in local_backward_frontier:
                        if can_exit or node in backward_exitable:
                            can_exit = True
                            break
                        for edge_id in outgoing_edges[node]:
                            edge = edges[edge_id]
                            if edge.to_location in locally_exitable: continue
                            variables['BACKTRACK_GOALS'] = edge.to_location, base_location
                            if edge.edge_id not in untraversable_edges or edge.satisfied(variables):
                                locally_exitable.add(edge.to_location)
                                new_locally_backward_exitable.add(edge.to_location)

                    local_backward_frontier.clear()
                    local_backward_frontier, new_locally_backward_exitable = new_locally_backward_exitable, local_backward_frontier

                # Restore Previous Variables Status
                for name, value in temp_variable_storage.items():
                    variables[name] = value
                temp_variable_storage.clear()
                variables['IS_BACKTRACKING'] = False
                variables['BACKTRACK_GOALS'] = None, None

                # If we can exit, set the corresponding variables to true.
                if can_exit:
                    if base_location in locations_set:
                        if not variables[base_location]:
                            current_level_part2.append(base_location)
                            #variables[base_location] = True
                    for item_location in data.item_locations_in_node[base_location]:
                        item_name = allocation.item_at_item_location[item_location]
                        if item_name == None: continue
                        if not variables[item_name]:
                            current_level_part2.append(item_name)
                            #variables[item_name] = True

            for node in current_level_part2:
                variables[node] = True

            if len(current_level_part1) == 0 and len(current_level_part2) == 0:
                break
            levels.append(current_level_part1)
            levels.append(current_level_part2)
            previous_new_variables.update(current_level_part2)

        if self.visualize:
            colors = [ \
                (255,191,0), (128,224,0), (0,160,0), (32,255,160), \
                (0,224,255), (0,160,255), (0,96,255), (128,96,255), \
                (160,32,224), (255,64,255), (255,128,160), (255,192,192), \
                (192,192,192), (160,160,160), (128,128,128), (64,64,64), \
                (32,32,32), (32,16,16), (32,0,0), (0,0,0) \
            ]
            template_edges = []
            for t in allocation.picked_templates:
                for c in t.changes:
                    template_edges.append(c.from_location + c.to_location)
            for edge in edges:
                if edge.from_location + edge.to_location in template_edges:
                    if edge.edge_id in untraversable_edges:
                        vis.set_edge_color(edge.from_location, edge.to_location, color=(255,32,255))
                    else:
                        vis.set_edge_color(edge.from_location, edge.to_location, color=(32,255,32))
                elif edge.edge_id in untraversable_edges:
                    vis.set_edge_color(edge.from_location, edge.to_location, color=(191,32,32))
            for loc in forward_enterable.intersection(backward_exitable):
                if loc in reachable_levels:
                    level = reachable_levels[loc]
                else:
                    level = 19
                level = min(level, 19)
                vis.set_node_color(loc, colors[level])
            vis.render()
        reachable = sorted(name for name, value in variables.items() if value)
        unreachable = sorted(name for name, value in variables.items() if not value)

        #if self.visualize:
            #for en, level in enumerate(levels):
                #print_ln('LEVEL %d' % en)
                #print_ln(level)

        return reachable, unreachable, levels, variables

    def analyze_with_variable_set(self, starting_variables):
        result, backward_exitable = self.verify_warps_reachable(starting_variables, diff_analysis=True)
        reachable, unreachable, levels, ending_variables = self.verify_reachable_items(starting_variables, backward_exitable)
        return reachable, unreachable, levels, ending_variables


