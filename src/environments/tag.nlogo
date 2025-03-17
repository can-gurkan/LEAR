extensions [ py table fp rnd ]

;;; TAG ENVIRONMENT
;;; This environment simulates a game of tag where:
;;; 1. 5 agents are randomly tagged at the start
;;; 2. Tagged agents (red) try to tag untagged agents (blue)
;;; 3. When a tagged agent touches an untagged agent, the tag is passed:
;;;    - The previously tagged agent becomes untagged
;;;    - The newly tagged agent becomes immune to being tagged by that specific agent for 20 ticks
;;; 4. At the end of each round, all tagged agents die and are replaced
;;;    by offspring of the survivors. One survivor at random is choosen to mutate their code.
;;;
;;; Fitness is determined by:
;;; - For untagged agents: accumulated distance from the nearest tagged agent (measured every 100 ticks)
;;;   with a significant bonus for surviving a generation
;;; - For tagged agents: accumulated proximity to untagged agents plus bonus points for each
;;;   successful tag before passing the tag to another agent
;;;
;;; Agent observations:
;;; - 3 directional views (left, center, right) in 120-degree cones:
;;;   - Center cone: -60° to 60° relative to the agent's heading
;;;   - Right cone: 60° to 180° relative to the agent's heading
;;;   - Left cone: -60° to -180° relative to the agent's heading
;;; - Each view returns info about the nearest agent: [distance, is-tagged?, relative-heading]
;;; - The agent's own tagged state
;;;
;;; Agents should develop strategies to:
;;; - When tagged: seek out and tag others to survive and maximize fitness
;;; - When untagged: maximize distance from tagged agents to build up fitness

__includes [
  "env_utils/evolution.nls"
  "env_utils/logging.nls"
  "config/tag-config.nls"
]

globals [
  generation
  init-rule
  generation-stats
  best-rule
  best-rule-fitness
  error-log
  tag-distance-threshold
  generation-length    ;; New global to separate round from generation concepts

  ;selection
  ;num-parents
  ;tournament-size
  ;selection-pressure
]

breed [llm-agents llm-agent]

llm-agents-own [
  input ;; observation vector
  rule ;; current rule (llm-generated)
  energy ;; current score
  lifetime ;; age of the agent (in generations)
  tagged? ;; whether the agent is currently tagged
  survival-time ;; how long the agent has survived
  parent-id ;; who number of parent
  parent-rule ;; parent rule
  immunity-timer ;; timer for immunity after being untagged (replaces immunities table)
  distance-score ;; accumulated distance score for fitness calculation
  tags-made ;; number of successful tags made (for tagged agents)

  ;; New variables for separate fitness tracking
  tagged-distance-score   ;; accumulated distance score while tagged
  untagged-distance-score ;; accumulated distance score while untagged
  time-spent-tagged       ;; ticks spent in tagged state
  time-spent-untagged     ;; ticks spent in untagged state

  ;; Direct access to observation data (semantic variable names)
  left-agent-distance     ;; distance to nearest agent on left
  left-agent-is-tagged?   ;; is the nearest agent on left tagged?
  left-agent-heading      ;; relative heading to nearest agent on left

  center-agent-distance   ;; distance to nearest agent in center
  center-agent-is-tagged? ;; is the nearest agent in center tagged?
  center-agent-heading    ;; relative heading to nearest agent in center

  right-agent-distance    ;; distance to nearest agent on right
  right-agent-is-tagged?  ;; is the nearest agent on right tagged?
  right-agent-heading     ;; relative heading to nearest agent on right

  ;; potential experimentation: provide multiple agent distances and headings within a radius
  ;; would be a vector, each element in the vector represents the agent and have the same information, distance, is-tagged, relative heading
  ;; for the closest n agents within a radius
]

;;; Setup Procedures

to setup-params
  if use-config-file? [
    carefully [
      run word "setup-params-" config-file
    ] [
      user-message word config-file " is not a valid config file."
    ]
  ]

  set tag-distance-threshold 1  ;; distance within which tagging occurs
  set tagged-time-penalty-factor 0.5 ;; default penalty factor if not set by slider
end

to setup-llm-agents
  create-llm-agents num-llm-agents [
    set color blue
    set shape "person"  ;; Use person shape instead of default
    set size 1.5       ;; Make agents a bit larger
    setxy random-xcor random-ycor  ;; Initial random placement (will be re-arranged)
    set rule init-rule
    set parent-id "na"
    set parent-rule "na"
    set tagged? false
    set immunity-timer 0
    init-agent-params
  ]

  ;; Randomly tag agents at the start based on slider value
  ask n-of initial-tagged-agents llm-agents [
    set tagged? true
    set color red
  ]

  ;; Use the same formation as during evolution
  arrange-agents-in-formation
end

to init-agent-params
  set energy 0
  set survival-time 0
  set lifetime 0
  set distance-score 0
  set tags-made 0
  set immunity-timer 0

  ;; Initialize the new tracking variables
  set tagged-distance-score 0
  set untagged-distance-score 0
  set time-spent-tagged 1
  set time-spent-untagged 1
end

to setup
  clear-all

  py:setup py:python
  py:run "import os"
  py:run "import sys"
  py:run "from pathlib import Path"
  py:run "sys.path.append(os.path.dirname(os.path.abspath('..')))"
  py:run "from src.mutation.mutate_code import mutate_code"

  set init-rule "lt random 360 fd 1"
  set generation-stats []
  set error-log []
  set best-rule-fitness 0
  set generation-length 1000  ;; Initialize the generation length (default 1000 ticks)

  ;; Create a playground-like environment
  setup-playground

  setup-params
  setup-llm-agents
  if logging? [ setup-logger ]
  reset-ticks
end

;; Create a playground environment for the tag game
to setup-playground
  ;; Set background color to represent grass/field
  ask patches [
    set pcolor 58  ;; Light green for grassy field
  ]

  ;; Create a playground boundary
  ask patches with [
    abs pxcor = max-pxcor or
    abs pxcor = max-pxcor - 1 or
    abs pycor = max-pycor or
    abs pycor = max-pycor - 1
  ] [
    set pcolor 36  ;; Darker green for boundary
  ]
end

;;; Go Procedures

to go
  do-plotting

  ;; Handle any delayed actions (like visual effects)
  handle-delayed-actions

  ;; Update immunity timers
  ask llm-agents [
    ;; Decrement immunity timer if it's active
    if immunity-timer > 0 [
      set immunity-timer immunity-timer - 1
    ]

    ;; Visual indicator for immunity - use target shape when immune
    ifelse immunity-timer > 0 [
      set shape "target"  ;; Use target shape to show immunity
    ] [
      set shape "person"  ;; Return to person shape when not immune
    ]
  ]

  ask llm-agents [
    set lifetime lifetime + 1
    set survival-time survival-time + 1

    ;; Update time spent in each state
    ifelse tagged? [
      set time-spent-tagged time-spent-tagged + 1
    ] [
      set time-spent-untagged time-spent-untagged + 1
    ]

    set input get-observation
    run-rule
    check-tagging
  ]
  update-fitness-scores

  ;; Update fitness scores at the end of each round
  if ticks >= 1 and ticks mod ticks-per-generation = 0 [
    evolve-agents

    ;; Position agents: tagged at center, untagged in a circle
    arrange-agents-in-formation
  ]

  tick
end

to run-rule
  carefully [
    ;; Enforce the maximum movement distance of 1
    let initial-xcor xcor
    let initial-ycor ycor

    run rule

    ;; Calculate the distance moved
    let dist-moved sqrt ((xcor - initial-xcor) ^ 2 + (ycor - initial-ycor) ^ 2)

    ;; If moved more than 1, scale back the movement
    if dist-moved > 1 [
      setxy initial-xcor + (xcor - initial-xcor) / dist-moved
            initial-ycor + (ycor - initial-ycor) / dist-moved
    ]
    ;; TODO: make parameter if the world can be wrapped or not
    ;; disable playground effect if not wrapped

    ;; NOTE: What happens if you take out movement restriction, both here and in the prompt

  ] [
    let error-info (word
      "ERROR WHILE RUNNING RULE: " rule
      " | Agent: " who
      " | Tick: " ticks
      " | Fitness: " fitness
      " | Lifetime: " lifetime
      " | Tagged: " tagged?
      " | Input: " input
    )
    if ticks mod generation-length = 1 [
      print error-info
      set error-log lput error-info error-log
    ]
  ]
end

to check-tagging
  ;; Only tagged agents can tag others
  if not tagged? [ stop ]

  ;; Find agents within tagging distance
  let potential-targets llm-agents in-radius tag-distance-threshold with [
    not tagged? and      ;; only tag untagged agents
    immunity-timer = 0   ;; not immune
  ]

  if any? potential-targets [
    let target one-of potential-targets
    let my-id who  ;; Store the current agent's ID

    ;; Tag the target
    ask target [
      set tagged? true
      set color red

      ;; Store tagger's ID to implement mutual immunity
      let target-id who

      ;; Make the target immune to the tagger for immunity-duration ticks
      set immunity-timer immunity-duration

      ;; Make the tagger immune to the tagged agent too (reciprocal immunity)
      ask llm-agent my-id [
        set immunity-timer immunity-duration
      ]
    ]

    ;; Count successful tags
    set tags-made tags-made + 1

    ;; Untag the tagger (pass the tag along)
    set tagged? false
    set color blue
  ]
end

;; This procedure should be called every tick to handle delayed actions
to handle-delayed-actions
  ask patches with [plabel != ""] [
    let revert-tick plabel
    let original-color plabel-color

    if is-number? revert-tick and ticks >= revert-tick [
      set pcolor original-color
      set plabel ""
    ]
  ]
end

to evolve-agents
  if ticks >= 1 and ticks mod ticks-per-generation = 0 [
    print word "\nGeneration: " generation

    ;; Select parents based on fitness (not just survivors)
    let parents select-agents
    let kill-num length parents

    ;; Track which agents to kill and which are the best
    let kill-dict agent-dict min-n-of kill-num llm-agents [fitness]
    let best-dict agent-dict turtle-set parents
    let new-agent-ids []

    ;; Create new offspring from parents and mutate them
    foreach parents [ parent ->
      ask parent [
        let my-parent-id who
        hatch 1 [
          set tagged? false
          set color blue
          set parent-id my-parent-id
          set parent-rule rule

          ;; Add the mutated label and mutate the rule
          set label "mutated"
          print (word "Mutating rule for agent " who ": " rule)
          set rule mutate-rule

          init-agent-params
          set new-agent-ids lput who new-agent-ids
        ]
      ]
    ]

    ;; Kill the least fit agents, but don't kill newly created offspring
    ask min-n-of kill-num llm-agents with [not member? who new-agent-ids] [fitness] [ die ]

    ;; Prepare data for logging
    let new-dict agent-dict llm-agents with [member? who new-agent-ids]
    update-generation-stats
    log-metrics (list best-dict new-dict kill-dict)

    print (word "After evolution - Total agents: " count llm-agents)

    ;; Reset agent states for the next generation
    ask llm-agents [
      set tagged? false
      set color blue

      ;; Conditionally reset fitness metrics based on the switch
      if reset-fitness-between-rounds? [
        set tagged-distance-score 0
        set untagged-distance-score 0
        set tags-made 0
        set time-spent-tagged 1  ;; Set to 1 to avoid division by zero
        set time-spent-untagged 1 ;; Set to 1 to avoid division by zero
      ]
    ]

    ;; Tag some agents at random to start the next generation
    ask n-of initial-tagged-agents llm-agents [
      set tagged? true
      set color red
    ]

    ;; Position agents properly for the next round
    arrange-agents-in-formation
  ]
end

;; Position agents with tagged at center and untagged in a surrounding circle
to arrange-agents-in-formation
  ;; First place tagged agents at the center
  ask llm-agents with [tagged?] [
    setxy 0 0
  ]

  ;; Get the untagged agents
  let untagged-agents llm-agents with [not tagged?]
  let num-untagged count untagged-agents

  if num-untagged > 0 [
    ;; Create a set of patches in a circle to use as positions
    let circle-patches patches with [
      ;; Create a circle of patches at ~70% of max radius
      round sqrt (pxcor ^ 2 + pycor ^ 2) = round (max-pxcor * 0.7)
    ]

    ;; If we have more agents than patches in our circle, add more patches
    if count circle-patches < num-untagged [
      set circle-patches patches with [
        round sqrt (pxcor ^ 2 + pycor ^ 2) >= round (max-pxcor * 0.65) and
        round sqrt (pxcor ^ 2 + pycor ^ 2) <= round (max-pxcor * 0.75)
      ]
    ]

    ;; Select n patches evenly distributed around the circle
    let positions n-of (min list num-untagged count circle-patches) circle-patches

    ;; Now place each untagged agent on one of these positions
    (foreach (sort untagged-agents) (sort positions) [ [agent pos] ->
      ask agent [
        setxy [pxcor] of pos [pycor] of pos
        ;; Add tiny random offset to avoid perfect overlap
        setxy xcor + random-float 0.4 - 0.2 ycor + random-float 0.4 - 0.2
      ]
    ])
  ]
end

;;; Helpers and Observable Reporters

to-report fitness
  ;; Normalize fitness by dividing each component by its mean before adding
  ;; This ensures neither component dominates the overall fitness

  let normalized-tagged 0
  let normalized-untagged 0

  ;; Calculate mean fitness values for both states (avoiding division by zero)
  let mean-tagged mean-tagged-fitness
  let mean-untagged mean-untagged-fitness

  ;; Calculate the penalty factor based on time spent tagged
  let tagged-time-ratio time-spent-tagged / (time-spent-tagged + time-spent-untagged)
  let penalty-factor 1 - (tagged-time-ratio * tagged-time-penalty-factor)

  ;; Apply the penalty directly to the tagged fitness normalization
  ifelse time-spent-tagged > 1 [
    set normalized-tagged ifelse-value (mean-tagged > 0)
      [(tagged-fitness / mean-tagged) * penalty-factor]
      [tagged-fitness * penalty-factor]
  ] [
    ;; If agent has no tagged experience, use the mean value
    set normalized-tagged 1
  ]

  ;; Set normalized untagged fitness
  ifelse time-spent-untagged > 1 [
    set normalized-untagged ifelse-value (mean-untagged > 0)
      [untagged-fitness / mean-untagged]
      [untagged-fitness]
  ] [
    ;; If agent has no untagged experience, use the mean value
    set normalized-untagged 1
  ]

  ;; Return the sum of normalized components
  report normalized-tagged + normalized-untagged
end

;; Report mean tagged fitness across all agents with tagged experience
to-report mean-tagged-fitness
  let tagged-agents llm-agents with [time-spent-tagged > 1]
  ifelse any? tagged-agents
    [report mean [tagged-fitness] of tagged-agents]
    [report 1]  ;; Return 1 if no agents have been tagged (neutral value for division)
end

;; Report mean untagged fitness across all agents with untagged experience
to-report mean-untagged-fitness
  let untagged-agents llm-agents with [time-spent-untagged > 1]
  ifelse any? untagged-agents
    [report mean [untagged-fitness] of untagged-agents]
    [report 1]  ;; Return 1 if no agents have been untagged (neutral value for division)
end

to-report mean-fitness
  report mean [fitness] of llm-agents
end

to-report get-observation
  ;; Return observations about nearby agents and own state
  let view-dist 10
  let view-angle 120
  let obs []

  ;; Observe in 3 directions (left, center, right) and set semantic variables
  ;; Center cone: -60° to 60°, Right cone: 60° to 180°, Left cone: -60° to -180°
  let directions [["left" -120] ["center" 0] ["right" 120]]
  let i 0

  foreach directions [ dir ->
    let dir-name first dir
    let angle last dir

    rt angle
    let cone-data get-agents-in-cone view-dist view-angle
    set obs lput cone-data obs

    ;; Set the semantic variables based on direction
    if dir-name = "left" [
      set left-agent-distance item 0 cone-data
      set left-agent-is-tagged? item 1 cone-data
      set left-agent-heading item 2 cone-data
    ]
    if dir-name = "center" [
      set center-agent-distance item 0 cone-data
      set center-agent-is-tagged? item 1 cone-data
      set center-agent-heading item 2 cone-data
    ]
    if dir-name = "right" [
      set right-agent-distance item 0 cone-data
      set right-agent-is-tagged? item 1 cone-data
      set right-agent-heading item 2 cone-data
    ]

    lt angle  ;; Reset heading
  ]

  ;; Add tagged state as the 4th element
  set obs lput tagged? obs

  report obs
end

to-report get-agents-in-cone [dist angle]
  let visible-agents other llm-agents in-cone dist angle
  let nearest-agent min-one-of visible-agents [distance myself]

  let result []

  ifelse nearest-agent != nobody [
    ;; Return distance to nearest, whether it's tagged, and heading towards/away
    let dist-to-agent distance nearest-agent
    let agent-tagged? [tagged?] of nearest-agent
    let relative-heading 0

    ;; Only calculate heading if not at same position (avoid "no heading defined" error)
    ifelse dist-to-agent > 0 [
      set relative-heading towards nearest-agent
    ] [
      ;; If at same position, use current heading as default
      set relative-heading heading
    ]

    set result (list
      dist-to-agent
      agent-tagged?
      relative-heading
    )
  ] [
    ;; No agent visible
    set result (list 0 false 0)
  ]

  report result
end

to-report get-generation-metrics
  let keys ["generation" "best rule" "mean fitness" "best fitness" "percent-tagged" "error log"]
  let values ifelse-value any? llm-agents [
    (list
      generation
      best-rule
      mean-fitness
      max [fitness] of llm-agents
      ((count llm-agents with [tagged?] / count llm-agents) * 100)
      error-log)
  ] [
    (list generation "na" 0 0 0 [])
  ]
  report fp:zip keys values
end

;;; Plotting

to do-plotting
  if ticks mod 10 = 0 [
    set-current-plot "Fitness Metrics"
    set-current-plot-pen "Mean Fitness"
    plot mean [fitness] of llm-agents

    set-current-plot-pen "Max Fitness"
    plot max [fitness] of llm-agents

    ;; Update the new plot for tagged/untagged fitness
    set-current-plot "Tagged vs Untagged Fitness (Amortized)"

    ;; Only plot if there are agents in each state
    if any? llm-agents with [time-spent-tagged > 0] [
      set-current-plot-pen "Tagged Fitness"
      plot mean-tagged-fitness
    ]

    if any? llm-agents with [time-spent-untagged > 0] [
      set-current-plot-pen "Untagged Fitness"
      plot mean-untagged-fitness
    ]

    ;; Plot the ratio of time spent in each state
    set-current-plot "Time in Each State"
    let total-agents count llm-agents
    if total-agents > 0 [
      set-current-plot-pen "Time Tagged"
      plot mean [time-spent-tagged] of llm-agents

      set-current-plot-pen "Time Untagged"
      plot mean [time-spent-untagged] of llm-agents
    ]
  ]
end

;; New procedure to update fitness scores based on distance from tagged agents
to update-fitness-scores
  ;; For untagged agents: reward them for being far from tagged agents
  ask llm-agents with [not tagged?] [
    let nearest-tagged min-one-of (llm-agents with [tagged?]) [distance myself]

    if nearest-tagged != nobody [
      let dist distance nearest-tagged
      set untagged-distance-score (dist + untagged-distance-score)
    ]

  ]

  ;; For tagged agents: reward them primarily based on proximity to untagged agents
  ask llm-agents with [tagged?] [
    let nearest-untagged min-one-of (llm-agents with [not tagged?]) [distance myself]

    if nearest-untagged != nobody [
      let dist distance nearest-untagged
      ;; Lower distance means better fitness (proximity-based), scale from 1-20
      let proximity-score 20 - (min list dist 20)
      set tagged-distance-score (tagged-distance-score + proximity-score)
    ]
  ]
end

;; Add reporters for getting tagged and untagged fitness separately
to-report tagged-fitness
  report tagged-distance-score / time-spent-tagged
end

to-report untagged-fitness
  report untagged-distance-score / time-spent-untagged
end

; TAGGED
;; 5 distance away from a untagged - 15
;; 20 distance away - 0

; 2 agents
; 1 has a really poor untagged rule but luckily stays untagged the entire time - really high untagged-fitness
; 1 has a really good untagged rule but unluckily stays tagged most of the time but gets untagged at the end - really low untagged-fitness


@#$#@#$#@
GRAPHICS-WINDOW
210
10
647
448
-1
-1
13.0
1
10
1
1
1
0
1
1
1
-16
16
-16
16
1
1
1
ticks
30.0

BUTTON
20
190
90
223
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
100
190
170
223
NIL
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
20
20
195
53
num-llm-agents
num-llm-agents
0
100
10.0
1
1
NIL
HORIZONTAL

SWITCH
20
240
195
273
llm-mutation?
llm-mutation?
0
1
-1000

PLOT
680
220
1090
370
Fitness Metrics
ticks
fitness
0.0
2.0
0.0
2.0
true
true
"" ""
PENS
"Mean Fitness" 1.0 0 -10899396 true "" ""
"Max Fitness" 1.0 0 -2674135 true "" ""

PLOT
685
65
1090
215
Tagged vs Untagged Fitness (Amortized)
ticks
fitness per tick
0.0
2.0
0.0
2.0
true
true
"" ""
PENS
"Tagged Fitness" 1.0 0 -2674135 true "" ""
"Untagged Fitness" 1.0 0 -13345367 true "" ""

PLOT
680
385
1090
535
Time in Each State
ticks
time
0.0
1000.0
0.0
1000.0
true
true
"" ""
PENS
"Time Tagged" 1.0 0 -2674135 true "" ""
"Time Untagged" 1.0 0 -13345367 true "" ""

SLIDER
20
100
195
133
ticks-per-generation
ticks-per-generation
100
2000
1000.0
100
1
NIL
HORIZONTAL

MONITOR
680
10
757
55
NIL
generation
17
1
11

CHOOSER
20
320
195
365
llm-type
llm-type
"groq" "claude" "deepseek" "gpt-4o"
1

SWITCH
20
140
195
173
logging?
logging?
0
1
-1000

SWITCH
20
280
195
313
text-based-evolution
text-based-evolution
1
1
-1000

SWITCH
400
470
575
503
reset-fitness-between-rounds?
reset-fitness-between-rounds?
0
1
-1000

SLIDER
400
510
575
543
immunity-duration
immunity-duration
0
30
10.0
1
1
ticks
HORIZONTAL

SLIDER
400
550
575
583
tagged-time-penalty-factor
tagged-time-penalty-factor
0
2
0.5
0.1
1
NIL
HORIZONTAL

INPUTBOX
20
370
195
430
experiment-name
tag-experiment
1
0
String

CHOOSER
20
470
195
515
selection
selection
"tournament" "fitness-prop"
1

SLIDER
20
520
195
553
num-parents
num-parents
0
10
1.0
1
1
NIL
HORIZONTAL

SLIDER
20
560
195
593
tournament-size
tournament-size
0
50
50.0
1
1
NIL
HORIZONTAL

SLIDER
20
600
195
633
selection-pressure
selection-pressure
0
1
0.65
0.01
1
NIL
HORIZONTAL

SLIDER
20
60
195
93
initial-tagged-agents
initial-tagged-agents
1
20
2.0
1
1
NIL
HORIZONTAL

SWITCH
210
470
385
503
use-config-file?
use-config-file?
1
1
-1000

INPUTBOX
210
510
385
570
config-file
default
1
0
String

MONITOR
780
10
877
55
Tagged Agents
count llm-agents with [tagged?]
17
1
11

MONITOR
880
10
997
55
Untagged Agents
count llm-agents with [not tagged?]
17
1
11

@#$#@#$#@
## WHAT IS IT?

This model simulates a game of tag among agents whose behaviors evolve over time. Agents try to either tag others (when they are tagged) or avoid being tagged (when they are not tagged). The evolution is powered by language models (LLMs) that generate and refine the rules governing agent behavior.

The simulation takes place in a bounded playground-like environment where agents cannot move beyond the borders, creating a realistic tag game scenario.

## HOW IT WORKS

At the start of each generation:
- A configurable number of agents (set by `initial-tagged-agents` slider, default 5) are randomly selected to be "tagged" (shown in red)
- Tagged agents try to touch untagged agents
- When a tagged agent touches an untagged agent, the untagged agent becomes tagged and the tagger becomes untagged
- The newly tagged agent becomes immune to the former tagger for 20 ticks
- Every ticks-per-round ticks, fitness scores are updated based on distance from tagged/untagged agents
- At the end of each round, one random surviving agent's rule is mutated
- After a full generation (1000 ticks by default), all tagged agents "die" and are replaced by offspring of successful (untagged) agents

Fitness calculation:
- For untagged agents: Higher is better, accumulates distance from tagged agents
- For tagged agents: Higher is better, rewards proximity to potential targets and successful tags
- Surviving a full generation provides a significant fitness bonus

Each agent knows:
- What other agents they can see within a 30-degree cone in 3 directions (left, center, right)
- For each direction, they have direct access to the nearest agent's distance, tagged status, and relative heading
- Whether they are currently tagged

Visual indicators:
- Red agents are tagged (trying to tag others)
- Blue agents are untagged (trying to avoid being tagged)
- Agents with immunity are shown with a "target" shape
- A yellow flash appears when one agent tags another

## HOW TO USE IT

1. Set the number of agents using the `num-llm-agents` slider (default is 100)
2. Set the number of initially tagged agents using the `initial-tagged-agents` slider (default is 5)
3. Choose whether to use LLM-based mutation with the `llm-mutation?` switch
4. Set the frequency of mutation with `ticks-per-round` (default is 100)
5. Press `setup` to initialize the simulation
6. Press `go` to run the simulation
7. Watch as agents evolve strategies for tagging or avoiding being tagged

## THINGS TO NOTICE

- How do agent strategies evolve over time?
- Do agents develop different behaviors when tagged versus not tagged?
- What emergent patterns of movement do you observe?
- Do agents learn to coordinate or develop evasion tactics?

## THINGS TO TRY

- Change the number of agents and observe how population density affects strategy
- Adjust the number of initially tagged agents to change the difficulty and dynamics of the simulation
- Toggle between LLM-based mutation and text-based evolution
- Try different LLM models to see if strategy evolution differs
- Modify the tag-distance-threshold or tag-immunity-duration to see how it affects gameplay
- Change the ticks-per-round to see how mutation frequency affects evolution

## EXTENDING THE MODEL

- Add energy requirements so agents must balance hunting/fleeing with obtaining resources
- Create environmental obstacles that agents can hide behind
- Add different agent types with varying abilities
- Implement a more complex immunity system based on agent relationships

## NETLOGO FEATURES

This model uses:
- Breed-specific variables to track agent state
- LLM-based rule generation and mutation
- Tables to store agent immunity relationships
- In-cone detection for agent visibility
- Dynamic visualization of agent states through color

## CREDITS AND REFERENCES

This model is part of the LEAR (Language-Enabled Agent Research) project, exploring how language models can enable evolving agent behaviors in simulated environments.
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.4.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
