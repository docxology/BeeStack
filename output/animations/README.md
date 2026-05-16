# Output Animations

Generated GIF animations for BeeBody, BeeBrain, BeeMind, BeeSwarm, and
BeeNiche. BeeBody has two real FlyBody locomotion renders: walking through
`WalkImitation` and flight through `FlightImitationWBPG` with
`WingBeatPatternGenerator`, both using
`flybody_bee/assets/apis_mellifera_worker.xml`.

BeeSwarm includes one reduced recruitment-field animation plus two strict
FlyBody/MuJoCo production scenes: ten BeeBody 3D models colliding with actual
bee-bee contacts, and a configured BeeBody 3D waggle dance with floor/body
contacts. Scene XMLs and contact metrics live under
`output/animations/flybody_scenes/`. Contact sheets are written beside every
GIF. The animation manifest, waggle-dance configuration, visual scores, contact
physics summaries, and accessibility text live at
`output/data/animation_manifest.json`.
