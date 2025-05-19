extensions [ py table fp rnd palette ]

__includes [
  "env_utils/evolution.nls"
  "env_utils/logging.nls"
  "env_utils/prompt_config.nls"
  "config/qd-sampling-config.nls"
]

globals [
  generation
  time-steps
  init-rule
  init-pseudocode
  generation-stats
  best-rule
  best-rule-fitness
  error-log
]

breed [llm-agents llm-agent]
breed [food-sources food-source]

patches-own [
 value
]

llm-agents-own [
  input ;; observation vector
  ;energy-ahead
  ;energy-left
  ;energy-right
  energy-ahead-close
  energy-left-close
  energy-right-close

  energy-ahead-medium
  energy-left-medium
  energy-right-medium

  energy-ahead-far
  energy-left-far
  energy-right-far
  rule ;; current rule (llm-generated)
  energy ;; current score
  novelty ;; behavioral novelty score
  lifetime ;; age of the agent (in generations)
  bd ;; behavior descriptor
  parent-id ;; who number of parent
  parent-rule ;; parent rule
  pseudocode ;; descriptive text rule
  parent-pseudocode ;; pseudocode associated with the parent
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
end

to-report get-additional-params
  report (list
    list "num-sources" num-sources
    list "init-rule" init-rule
    list "init-pseudocode" init-pseudocode
    list "alpha" alpha
    list "landscape-func" landscape-func
  )
end

to setup-llm-agents
  create-llm-agents num-llm-agents [
    set color red
    set size 2
    set heading 0
    ;setxy random-xcor random-ycor
    set rule init-rule
    set parent-id "na"
    set parent-rule "na"
    set pseudocode init-pseudocode
    set parent-pseudocode "na"
    init-agent-params ;; Init with zero energy
  ]
end

to init-agent-params
  set energy 0
  set bd []
  set lifetime 0
end

to setup-landscape-simple
  let min-val 1
  let max-val 50
  let diff-amount 0.8
  let diff-rep 20

  ask patches [set value min-val]

  let r (world-width / 2) - 10
  let angle 360 / num-sources
  foreach range num-sources [ i ->
    let x r * cos (angle * i)
    let y r * sin (angle * i)
    ask patch x y [ set value max-val ]
  ]
  repeat diff-rep [
    diffuse4 value diff-amount
  ]
  color-patches
end

to-report rastrigin [x y]
  let a 10
  let n 2
  let bound 3.12
  let scale bound / max-pxcor
  set x x * scale
  set y y * scale
  report sum map [z -> a + (z ^ 2 - a * cos (2 * pi * z * 180 / pi))] list x y
end

to-report drop-wave [x y]
  let a 12
  let b 2
  let bound 2
  let scale bound / max-pxcor
  set x x * scale
  set y y * scale
  report 0.65 + (-1 * (1 + cos (a * sqrt (x ^ 2 + y ^ 2) * 180 / pi)) / ((1 / b) * (x ^ 2 + y ^ 2) + b))
end

to-report eggholder [x y]
  let a 47
  let b 2
  let bound 600
  let scale bound / max-pxcor
  set x x * scale
  set y y * scale
  report -1 * (y + a) * sin (sqrt (abs (y + x / b + a)) * 180 / pi) - x * sin (sqrt (abs (x - (y + a))) * 180 / pi)
end

to-report sine-test [x0 y0]
  let bound 6
  let scale (bound / max-pxcor)
  let x x0 * scale
  let y y0 * scale
  report sin (x * 180 / pi) + sin (y * 180 / pi)
end

to-report get-landscape-func
  let fn landscape-func
  report (ifelse-value
    fn = "rastrigin" [[[x y] -> rastrigin x y]]
    fn = "drop-wave" [[[x y] -> drop-wave x y]]
    fn = "eggholder" [[[x y] -> eggholder x y]]
    fn = "sine-test" [[[x y] -> sine-test x y]]
  )
end

to setup-landscape-func
  let wsize 30
  let pscale 8.16 * 25
  resize-world (-1 * wsize) wsize (-1 * wsize) wsize
  set-patch-size pscale / wsize
  let func get-landscape-func
  ask patches [
    set value (runresult func pxcor pycor)
    ;set value rastrigin pxcor pycor
  ]
  normalize-patches
  color-patches
end

to normalize-patches
  let max-val max [value] of patches
  let min-val min [value] of patches
  ask patches [set value 2 * (safe-div (value - min-val) (max-val - min-val)) - 1]
end

to color-patches
  let sc-low -1 ;min [value] of patches ;-0.1
  let sc-high 1 ;max [value] of patches ; 2.2 ;2.2
  ;ask patches [set pcolor scale-color blue value sc-low sc-high]
  ask patches [set pcolor palette:scale-gradient [[0 180 30] [30 30 30] [20 80 255]] value sc-low sc-high]
end

to setup-archive
  py:run "from src.environments.env_utils.archive import *"
  py:set "threshold" acceptance-threshold
  py:set "desc_dim" bd-dim
  py:set "m_size" max-archive-size
  py:run "arch = Archive.create(acceptance_threshold=threshold, state_descriptor_size=desc_dim, max_size=m_size)"
  ;py:run "print(arch)"
end

to setup
  clear-all

  py:setup py:python
  py:run "import os"
  py:run "import sys"
  py:run "from pathlib import Path"
  py:run "sys.path.append(os.path.dirname(os.path.abspath('..')))"
  py:run "from src.mutation.mutate_code import mutate_code"

  ;setup-landscape
  setup-landscape-func

  set init-rule "lt random 20 rt random 20 fd 1"
  set init-pseudocode "Take left turn randomly within 0-20 degrees, then take right turn randomly within 0-20 degrees and move forward 1"

  set generation-stats []
  set error-log []
  set best-rule-fitness 0

  setup-llm-agents
  setup-params
  setup-archive
  if logging? [ setup-logger get-additional-params ]
  write-prompt-config prompt-type prompt-name
  reset-ticks
end

;;; Go Procedures

to go
  do-plotting
  ask llm-agents [
    set lifetime lifetime + 1
    get-observation
    run-rule
    harvest
    update-bd
  ]
  color-patches
  compute-novelty
  evolve-agents
  set time-steps time-steps + 1
  tick
end

to harvest
  let val [value] of patch-here
  set energy energy + val
  ask patch-here [set value 0]
;  if val > 0 [
;    set energy energy + val
;    ask patch-here [set value 0]
;  ]
end

to run-rule
  carefully [
    run rule
  ] [
    let error-info (word
      "ERROR WHILE RUNNING RULE: " rule
      " | Agent: " who
      " | Tick: " ticks
      " | Fitness: " fitness
      " | Lifetime: " lifetime
      " | Input: " input
      " | Error: " error-message
    )
    if ticks mod ticks-per-generation = 1 [
      if verbose? [ print error-info ]
      set error-log lput error-info error-log
    ]
  ]
end

to evolve-agents
  if ticks >= 1 and ticks mod ticks-per-generation = 0 [
    print word "\nGeneration: " generation

    let parents select-agents
    let kill-num length parents

    let kill-dict agent-dict min-n-of kill-num llm-agents [fitness]
    let best-dict agent-dict turtle-set parents
    let new-agent-ids []

    foreach parents [ parent ->
      ask parent [
        let my-parent-id who
        let my-rule rule
        let my-pseudocode pseudocode
        hatch 1 [
          set parent-id my-parent-id
          set parent-rule my-rule
          set parent-pseudocode my-pseudocode
          set rule mutate-rule
          init-agent-params
          set new-agent-ids lput who new-agent-ids
        ]
      ]
    ]

    ask min-n-of kill-num llm-agents with [not member? who new-agent-ids] [fitness] [ die ]

    let new-dict agent-dict llm-agents with [member? who new-agent-ids]
    update-generation-stats
    log-metrics (list best-dict new-dict kill-dict)
    set error-log []
    reset-env

  ]
end

to reset-env
  setup-landscape-func
  set time-steps 0
  ask llm-agents [
    set energy 0
    setxy 0 0
    set heading 0
    set novelty 0
    set bd []
  ]
end

to compute-novelty
  if ticks >= 1 and ticks mod ticks-per-generation = 0 [
    ;print [bd] of llm-agents
    py:set "desc_array" [bd] of llm-agents
    py:set "k_neighbors" k-neighbors
    ;py:run "print(desc_array)"
    py:run "arch = arch.insert(desc_array)"
    ;py:run "print(arch)"
    ask llm-agents [
      py:set "bd" bd
      set novelty py:runresult "score_euclidean_novelty(arch, bd, num_nearest_neighb = k_neighbors).item()"
      ;print novelty
    ]
  ]
end

;;; Helpers and Observable Reporters

to-report fitness
  let max-nov max [novelty] of llm-agents
  let min-nov min [novelty] of llm-agents
  let norm-novelty safe-div (novelty - min-nov) (max-nov - min-nov)
  let max-en max [energy] of llm-agents
  let min-en min [energy] of llm-agents
  let norm-energy safe-div (energy - min-en) (max-en - min-en)
  report (1 - alpha) * norm-energy + alpha * norm-novelty
end

to update-bd
  let time-gap floor (ticks-per-generation / bd-dim)
  if time-steps mod time-gap = 0 and time-steps > 0 [
    set bd lput energy bd
    ;print bd
  ]
  if ticks >= 1 and ticks mod ticks-per-generation = 0 [
    set bd normalize-bd bd
    ;print bd
  ]
end

to-report normalize-bd [vec]
  if-else length vec >= 2 [
    let i length vec - 1
    let new-vec []
    foreach range (length vec - 1) [ ->
      set new-vec fput (item i vec - item (i - 1) vec) new-vec
      set i i - 1
    ]
    set new-vec fput item 0 vec new-vec
    report new-vec ] [ report vec ]
end

to-report mean-fitness
  report mean [fitness] of llm-agents
end

to-report mean-energy
  report mean [energy] of llm-agents
end

to-report max-fitness
  report max [fitness] of llm-agents
end

to-report max-energy
  report max [energy] of llm-agents
end

to-report max-fit-agent-rule
  report [rule] of max-one-of llm-agents [fitness]
end

to-report max-energy-agent-rule
  report [rule] of max-one-of llm-agents [energy]
end

to get-observation
  let dist-gap 3
  set energy-ahead-close [value] of patch-ahead 1
  set energy-left-close  [value] of patch-left-and-ahead 90 1
  set energy-right-close [value] of patch-right-and-ahead 90 1

  set energy-ahead-medium [value] of patch-ahead 1 + dist-gap
  set energy-left-medium  [value] of patch-left-and-ahead 90 1 + dist-gap
  set energy-right-medium [value] of patch-right-and-ahead 90 1 + dist-gap

  set energy-ahead-far [value] of patch-ahead 1 + dist-gap * 2
  set energy-left-far  [value] of patch-left-and-ahead 90 1 + dist-gap * 2
  set energy-right-far [value] of patch-right-and-ahead 90 1 + dist-gap * 2
end

to-report get-generation-metrics
  let keys ["generation" "best rule" "mean fitness" "best fitness" "mean food" "error log"]
  let values ifelse-value any? llm-agents [
    (list
      generation
      best-rule
      mean-fitness
      max [fitness] of llm-agents
      mean [energy] of llm-agents
      error-log)
  ] [
    (list generation "na" 0 0 0 [])
  ]
  report fp:zip keys values
end

to-report safe-div [x y]
  report ifelse-value y = 0 [0] [x / y]
end


;;; Plotting

to do-plotting
  if ticks mod ticks-per-generation = 0 [
    set-current-plot "Mean Energy of Agents"
    set-current-plot-pen "Mean Energy"
    plotxy generation mean [energy] of llm-agents
    set-current-plot-pen "Max Energy"
    plotxy generation max [energy] of llm-agents
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
210
10
632
433
-1
-1
6.8
1
10
1
1
1
0
1
1
1
-30
30
-30
30
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
25
6.0
1
1
NIL
HORIZONTAL

SLIDER
20
60
195
93
num-sources
num-sources
0
20
3.0
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
60
1090
350
Mean Energy of Agents
generation
energy
0.0
5.0
0.0
10.0
true
true
"" ""
PENS
"Mean Energy" 1.0 0 -817084 true "" ""
"Max Energy" 1.0 0 -13345367 true "" ""

SLIDER
20
100
195
133
ticks-per-generation
ticks-per-generation
1
2000
200.0
1
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

INPUTBOX
20
370
195
430
experiment-name
sampling-test
1
0
String

CHOOSER
20
455
195
500
selection
selection
"tournament" "fitness-prop"
0

SLIDER
20
505
195
538
num-parents
num-parents
0
10
2.0
1
1
NIL
HORIZONTAL

SLIDER
20
545
195
578
tournament-size
tournament-size
0
50
6.0
1
1
NIL
HORIZONTAL

SLIDER
20
585
195
618
selection-pressure
selection-pressure
0
1
1.0
0.01
1
NIL
HORIZONTAL

SWITCH
210
455
385
488
use-config-file?
use-config-file?
1
1
-1000

INPUTBOX
210
495
385
555
config-file
default
1
0
String

SWITCH
400
455
575
488
verbose?
verbose?
0
1
-1000

INPUTBOX
210
560
385
620
prompt-type
sampling
1
0
String

INPUTBOX
210
625
385
685
prompt-name
zero_shot_code_wcomments
1
0
String

SLIDER
400
495
575
528
bd-dim
bd-dim
1
20
8.0
1
1
NIL
HORIZONTAL

SLIDER
400
575
575
608
max-archive-size
max-archive-size
1
10000
500.0
1
1
NIL
HORIZONTAL

SLIDER
400
535
575
568
acceptance-threshold
acceptance-threshold
0
20
2.0
0.1
1
NIL
HORIZONTAL

SLIDER
590
455
765
488
alpha
alpha
0
1
0.0
0.01
1
NIL
HORIZONTAL

SLIDER
590
495
765
528
k-neighbors
k-neighbors
0
20
15.0
1
1
NIL
HORIZONTAL

CHOOSER
680
365
855
410
landscape-func
landscape-func
"rastrigin" "drop-wave" "eggholder" "sine-test"
2

@#$#@#$#@
## WHAT IS IT?

(a general understanding of what the model is trying to show or explain)

## HOW IT WORKS

(what rules the agents use to create the overall behavior of the model)

## HOW TO USE IT

(how to use the model, including a description of each of the items in the Interface tab)

## THINGS TO NOTICE

(suggested things for the user to notice while running the model)

## THINGS TO TRY

(suggested things for the user to try to do (move sliders, switches, etc.) with the model)

## EXTENDING THE MODEL

(suggested things to add or change in the Code tab to make the model more complicated, detailed, accurate, etc.)

## NETLOGO FEATURES

(interesting or unusual features of NetLogo that the model uses, particularly in the Code tab; or where workarounds were needed for missing features)

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)
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
Circle -16777216 true false 24 174 42
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
<experiments>
  <experiment name="test-exp" repetitions="3" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="5000"/>
    <metric>generation</metric>
    <metric>mean-fitness</metric>
    <metric>max [fitness] of llm-agents</metric>
    <metric>best-rule-fitness</metric>
    <metric>best-rule</metric>
    <runMetricsCondition>ticks mod ticks-per-generation = 0</runMetricsCondition>
    <enumeratedValueSet variable="tournament-size">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-llm-agents">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection-pressure">
      <value value="0.85"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="use-config-file?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="logging?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-parents">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="config-file">
      <value value="&quot;default&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ticks-per-generation">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="text-based-evolution">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-mutation?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-food-sources">
      <value value="30"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="experiment-name">
      <value value="&quot;bspacetest&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection">
      <value value="&quot;tournament&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-type">
      <value value="&quot;claude&quot;"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="one-shot-code-exp" repetitions="10" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="150000"/>
    <metric>generation</metric>
    <metric>mean-fitness</metric>
    <metric>max [fitness] of llm-agents</metric>
    <metric>best-rule-fitness</metric>
    <metric>best-rule</metric>
    <runMetricsCondition>ticks mod ticks-per-generation = 0</runMetricsCondition>
    <enumeratedValueSet variable="tournament-size">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-llm-agents">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection-pressure">
      <value value="0.8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="use-config-file?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="logging?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-parents">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="config-file">
      <value value="&quot;default&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ticks-per-generation">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="text-based-evolution">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-mutation?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-food-sources">
      <value value="30"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="experiment-name">
      <value value="&quot;bspacetest&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection">
      <value value="&quot;tournament&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-type">
      <value value="&quot;claude&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="verbose?">
      <value value="false"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="two-shot-code-exp" repetitions="5" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="150000"/>
    <metric>generation</metric>
    <metric>mean-fitness</metric>
    <metric>max [fitness] of llm-agents</metric>
    <metric>best-rule-fitness</metric>
    <metric>best-rule</metric>
    <runMetricsCondition>ticks mod ticks-per-generation = 0</runMetricsCondition>
    <enumeratedValueSet variable="tournament-size">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-llm-agents">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection-pressure">
      <value value="0.8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="use-config-file?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="logging?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-parents">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="config-file">
      <value value="&quot;default&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ticks-per-generation">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="text-based-evolution">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-mutation?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-food-sources">
      <value value="30"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="experiment-name">
      <value value="&quot;two_shot_code_exp_opt&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection">
      <value value="&quot;tournament&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-type">
      <value value="&quot;groq&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="verbose?">
      <value value="false"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="zero-shot-code-exp" repetitions="6" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="150000"/>
    <metric>generation</metric>
    <metric>mean-fitness</metric>
    <metric>max [fitness] of llm-agents</metric>
    <metric>best-rule-fitness</metric>
    <metric>best-rule</metric>
    <runMetricsCondition>ticks mod ticks-per-generation = 0</runMetricsCondition>
    <enumeratedValueSet variable="tournament-size">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-llm-agents">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection-pressure">
      <value value="0.8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="use-config-file?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="logging?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-parents">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="config-file">
      <value value="&quot;default&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ticks-per-generation">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="text-based-evolution">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-mutation?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-food-sources">
      <value value="30"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="experiment-name">
      <value value="&quot;zero_shot_code_exp_groq&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection">
      <value value="&quot;tournament&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-type">
      <value value="&quot;groq&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="verbose?">
      <value value="false"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="zero-shot-code-wcomments-exp" repetitions="6" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="150000"/>
    <metric>generation</metric>
    <metric>mean-fitness</metric>
    <metric>max [fitness] of llm-agents</metric>
    <metric>best-rule-fitness</metric>
    <metric>best-rule</metric>
    <runMetricsCondition>ticks mod ticks-per-generation = 0</runMetricsCondition>
    <enumeratedValueSet variable="tournament-size">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-llm-agents">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection-pressure">
      <value value="0.8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="use-config-file?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="logging?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-parents">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="config-file">
      <value value="&quot;default&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ticks-per-generation">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="text-based-evolution">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-mutation?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-food-sources">
      <value value="30"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="experiment-name">
      <value value="&quot;zero_shot_code_wcomments_exp&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection">
      <value value="&quot;tournament&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-type">
      <value value="&quot;groq&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="verbose?">
      <value value="false"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="one-shot-code-wcomments-exp" repetitions="5" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="150000"/>
    <metric>generation</metric>
    <metric>mean-fitness</metric>
    <metric>max [fitness] of llm-agents</metric>
    <metric>best-rule-fitness</metric>
    <metric>best-rule</metric>
    <runMetricsCondition>ticks mod ticks-per-generation = 0</runMetricsCondition>
    <enumeratedValueSet variable="tournament-size">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-llm-agents">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection-pressure">
      <value value="0.8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="use-config-file?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="logging?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-parents">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="config-file">
      <value value="&quot;default&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ticks-per-generation">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="text-based-evolution">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-mutation?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-food-sources">
      <value value="30"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="experiment-name">
      <value value="&quot;one_shot_code_wcomments_exp&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection">
      <value value="&quot;tournament&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-type">
      <value value="&quot;groq&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="verbose?">
      <value value="false"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="two-shot-code-wcomments-exp" repetitions="5" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="150000"/>
    <metric>generation</metric>
    <metric>mean-fitness</metric>
    <metric>max [fitness] of llm-agents</metric>
    <metric>best-rule-fitness</metric>
    <metric>best-rule</metric>
    <runMetricsCondition>ticks mod ticks-per-generation = 0</runMetricsCondition>
    <enumeratedValueSet variable="tournament-size">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-llm-agents">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection-pressure">
      <value value="0.8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="use-config-file?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="logging?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-parents">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="config-file">
      <value value="&quot;default&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ticks-per-generation">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="text-based-evolution">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-mutation?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-food-sources">
      <value value="30"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="experiment-name">
      <value value="&quot;two_shot_code_wcomments_exp&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection">
      <value value="&quot;tournament&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-type">
      <value value="&quot;groq&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="verbose?">
      <value value="false"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="zero-shot-pseudocode-exp" repetitions="5" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="150000"/>
    <metric>generation</metric>
    <metric>mean-fitness</metric>
    <metric>max [fitness] of llm-agents</metric>
    <metric>best-rule-fitness</metric>
    <metric>best-rule</metric>
    <runMetricsCondition>ticks mod ticks-per-generation = 0</runMetricsCondition>
    <enumeratedValueSet variable="tournament-size">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-llm-agents">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection-pressure">
      <value value="0.8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="use-config-file?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="logging?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-parents">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="config-file">
      <value value="&quot;default&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ticks-per-generation">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="text-based-evolution">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-mutation?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-food-sources">
      <value value="30"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="experiment-name">
      <value value="&quot;zero_shot_pseudocode_exp&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection">
      <value value="&quot;tournament&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-type">
      <value value="&quot;groq&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="verbose?">
      <value value="false"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="one-shot-pseudocode-exp" repetitions="1" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="150000"/>
    <metric>generation</metric>
    <metric>mean-fitness</metric>
    <metric>max [fitness] of llm-agents</metric>
    <metric>best-rule-fitness</metric>
    <metric>best-rule</metric>
    <runMetricsCondition>ticks mod ticks-per-generation = 0</runMetricsCondition>
    <enumeratedValueSet variable="tournament-size">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-llm-agents">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection-pressure">
      <value value="0.8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="use-config-file?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="logging?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-parents">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="config-file">
      <value value="&quot;default&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ticks-per-generation">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="text-based-evolution">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-mutation?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-food-sources">
      <value value="30"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="experiment-name">
      <value value="&quot;one_shot_pseudocode_exp&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection">
      <value value="&quot;tournament&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-type">
      <value value="&quot;groq&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="verbose?">
      <value value="false"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="two-shot-pseudocode-exp" repetitions="5" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="150000"/>
    <metric>generation</metric>
    <metric>mean-fitness</metric>
    <metric>max [fitness] of llm-agents</metric>
    <metric>best-rule-fitness</metric>
    <metric>best-rule</metric>
    <runMetricsCondition>ticks mod ticks-per-generation = 0</runMetricsCondition>
    <enumeratedValueSet variable="tournament-size">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-llm-agents">
      <value value="10"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection-pressure">
      <value value="0.8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="use-config-file?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="logging?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-parents">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="config-file">
      <value value="&quot;default&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ticks-per-generation">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="text-based-evolution">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-mutation?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-food-sources">
      <value value="30"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="experiment-name">
      <value value="&quot;two_shot_pseudocode_exp&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection">
      <value value="&quot;tournament&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-type">
      <value value="&quot;groq&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="verbose?">
      <value value="false"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="qd-exp1" repetitions="10" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="10000"/>
    <metric>generation</metric>
    <metric>mean-fitness</metric>
    <metric>max-fitness</metric>
    <metric>mean-energy</metric>
    <metric>max-energy</metric>
    <metric>max-fit-agent-rule</metric>
    <metric>max-energy-agent-rule</metric>
    <metric>best-rule-fitness</metric>
    <metric>best-rule</metric>
    <runMetricsCondition>ticks mod ticks-per-generation = 0</runMetricsCondition>
    <enumeratedValueSet variable="tournament-size">
      <value value="6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="prompt-type">
      <value value="&quot;sampling&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="landscape-func">
      <value value="&quot;rastrigin&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-archive-size">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="alpha">
      <value value="0"/>
      <value value="0.25"/>
      <value value="0.5"/>
      <value value="0.75"/>
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-llm-agents">
      <value value="6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="k-neighbors">
      <value value="15"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="verbose?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection-pressure">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="use-config-file?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="logging?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-parents">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="bd-dim">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="config-file">
      <value value="&quot;default&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ticks-per-generation">
      <value value="200"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-sources">
      <value value="3"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="text-based-evolution">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-mutation?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="experiment-name">
      <value value="&quot;qd-rastrigin-test-exp&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-type">
      <value value="&quot;claude&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection">
      <value value="&quot;tournament&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="acceptance-threshold">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="prompt-name">
      <value value="&quot;zero_shot_code_wcomments&quot;"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="qd-exp-dw" repetitions="10" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="10000"/>
    <metric>generation</metric>
    <metric>mean-fitness</metric>
    <metric>max-fitness</metric>
    <metric>mean-energy</metric>
    <metric>max-energy</metric>
    <metric>max-fit-agent-rule</metric>
    <metric>max-energy-agent-rule</metric>
    <metric>best-rule-fitness</metric>
    <metric>best-rule</metric>
    <runMetricsCondition>ticks mod ticks-per-generation = 0</runMetricsCondition>
    <enumeratedValueSet variable="tournament-size">
      <value value="6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="prompt-type">
      <value value="&quot;sampling&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="landscape-func">
      <value value="&quot;drop-wave&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-archive-size">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="alpha">
      <value value="0"/>
      <value value="0.25"/>
      <value value="0.5"/>
      <value value="0.75"/>
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-llm-agents">
      <value value="6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="k-neighbors">
      <value value="15"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="verbose?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection-pressure">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="use-config-file?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="logging?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-parents">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="bd-dim">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="config-file">
      <value value="&quot;default&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ticks-per-generation">
      <value value="200"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-sources">
      <value value="3"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="text-based-evolution">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-mutation?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="experiment-name">
      <value value="&quot;qd-dw-exp&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-type">
      <value value="&quot;claude&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection">
      <value value="&quot;tournament&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="acceptance-threshold">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="prompt-name">
      <value value="&quot;zero_shot_code_wcomments&quot;"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="qd-exp-add" repetitions="10" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="10000"/>
    <metric>generation</metric>
    <metric>mean-fitness</metric>
    <metric>max-fitness</metric>
    <metric>mean-energy</metric>
    <metric>max-energy</metric>
    <metric>max-fit-agent-rule</metric>
    <metric>max-energy-agent-rule</metric>
    <metric>best-rule-fitness</metric>
    <metric>best-rule</metric>
    <enumeratedValueSet variable="tournament-size">
      <value value="6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="prompt-type">
      <value value="&quot;sampling&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="landscape-func">
      <value value="&quot;rastrigin&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="max-archive-size">
      <value value="500"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="alpha">
      <value value="0.75"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-llm-agents">
      <value value="6"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="k-neighbors">
      <value value="15"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="verbose?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection-pressure">
      <value value="1"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="use-config-file?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="logging?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-parents">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="bd-dim">
      <value value="8"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="config-file">
      <value value="&quot;default&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="ticks-per-generation">
      <value value="200"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="num-sources">
      <value value="3"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="text-based-evolution">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-mutation?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="experiment-name">
      <value value="&quot;qd-rastrigin-add-exp&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="llm-type">
      <value value="&quot;claude&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="selection">
      <value value="&quot;tournament&quot;"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="acceptance-threshold">
      <value value="2"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="prompt-name">
      <value value="&quot;zero_shot_code_wcomments&quot;"/>
    </enumeratedValueSet>
  </experiment>
</experiments>
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
1
@#$#@#$#@
