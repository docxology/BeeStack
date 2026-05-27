# Antennal movement responses to different plume structures in the honey bee, *Apis mellifera*

Dataset DOI: [10.5061/dryad.qjq2bvqw6](https://doi.org/10.5061/dryad.qjq2bvqw6)

## Description of the data and file structure

Data columns associated with Jernigan_etal_2026_JEB_activesensing_plumestructure_antennal_data.csv file associated with the publication at [https://doi.org/10.1242/jeb.250786](https://doi.org/10.1242/jeb.250786). See methods of associated publication for additional details. Column data are as follows. Antennal angle data extracted using SwarmSight software. See [http://swarmsight.org/](http://swarmsight.org/) for raw video extraction code and additional details.  All position and angle measures are reported in video pixel space, the camera and bee position was fixed across all animals and trials such that pixel size is equivalent across all trials.

### Files and variables

#### File: Jernigan_etal_2026_JEB_activesensing_plumestructure_antennal_data.csv

**Description:** 

##### Variables

* Bee: subjectID.
* Plume: plume condition, see Jernigan et al. 2026 [https://doi.org/10.1242/jeb.250786](https://doi.org/10.1242/jeb.250786) for additional details.
* speed: airflow speed in the presented wind tunnel in cm/s.
* Round: replicate presentation number for each plume and speed combination.
* Frame: Frame number. Starts with 1. Time can be determined by dividing this value by the video frame rate (30 fps).
* TreatmentSensor: Brightness value of the pixel in the center of the Treatment Sensor. Value ranges between 0 and 255, with 255 indicating maximum brightness.
* PER.X: The X position in pixels of the detected proboscis. If no proboscis is detected, the X values will point to the edge of the mandibles.
* PER.Y: The Y position in pixels  of the detected proboscis. If no proboscis is detected, the Y values will point to the edge of the mandibles.
* Left Sector: The 36-degree sector in pixels  (1-5) on either side of the head, which contained the largest number of likely antenna points. Can be useful if antenna x, y measures are too noisy. This is the coarsest, but most reliable antenna orientation measure.
* RightSector: The 36-degree sector in pixels  (1-5) on either side of the head, which contained the largest number of likely antenna points. Can be useful if antenna x, y measures are too noisy. This is the coarsest, but most reliable antenna orientation measure.
* LeftFlagellumTip.X: The X position in pixels  of the tip of the left antenna in the video frame.
* LeftFlagellumTip.Y: The Y position in pixels of the tip of the left antenna in the video frame.
* RightFlagellumTip.X: The X position in pixels of the tip of the right antenna in the video frame.
* RightFlagellumTip.Y: The Y position in pixels of the tip of the right antenna in the video frame
* LeftFlagellumBase.X: The X position in pixels of the base of the left antenna flagellum that did not overlap the head.
* LeftFlagellumBase.Y: The Y position in pixels of the base of the left antenna flagellum that did not overlap the head.
* RightFlagellumBase.X: The X position in pixels of the base of the right antenna flagellum that did not overlap the head.
* RightFlagellumBase.Y: The Y position in pixels of the base of the right antenna flagellum that did not overlap the head.
* RotationAngle: The angle, in degrees, that the head was rotated. 0 means the head pointed directly to the top of the screen. Positive values indicate clockwise rotation, negative - counterclockwise.
* AntennaSensorWidth: The width, in video pixels, of the boundaries of the square Antenna Sensor widget from SwarmSight software.
* AntennaSensorHeight: See AntennaSensorWidth. Height = Width.
* AntennaSensorOffset.X: X value indicates the distance in pixels  between the left-most edge of the video to the left-most edge of the AntennaSensor widget from SwarmSight Software.
* AntennaSensorOffset.Y: Y value indicates the distance in pixels between the left-most edge of the video to the left-most edge of the AntennaSensor widget from SwarmSight Software.
* AntennaSensorScale.X: X Scale factor of the AntennaSensor in arbitrary units from the SwarmSight software.
* AntennaSensorScale.Y: Y Scale factor of the AntennaSensor in arbitrary units from the SwarmSight software.
* Odor_detector: On versus off, from the detector of whether odor was being presented or not.
* CenterX: X location in pixels  from the video of the center of the bee's head.
* CenterY: Y location in pixels from the video of the center of the bee's head.
* LeftTipRelToCenterX: X location in pixels from video of left antenna tip relative to CenterX.
* LeftTipRelToCenterY: Y location in pixels  from video of left antenna tip relative to CenterY.
* RightTipRelToCenterX: X location in pixels from video of right antenna tip relative to CenterX.
* RightTipRelToCenterY: Y location in pixels from video of right antenna tip relative to CenterY
* LeftTheta: computed antennal angle of left antenna relative to the center and rotation angle.
* RightTheta: computed antennal angle of the right antenna relative to the center and rotation angle.
* LeftD: estimated height in pixels above the head of the tip of the left antenna. See the methods paper associated with SwarmSight for the calculation.
* RightD: estimated height in pixels above the head of the tip of the right antenna. See the methods paper associated with SwarmSight for the calculation.
* LeftRTcrit: statistically significant threshold of the radius, R, using a 97.5% confidence threshold value of estimated height D for the left antenna.
* RightRTcrit: statistically significant threshold of the radius, R, using a 97.5% confidence threshold value of estimated height D for the right antenna.
* LeftPhi: estimated angle above the head based upon D and R in previous columns for left antenna.
* RightPhi: estimated angle above the head based upon D and R in previous columns for right antenna.
* deriv1RightTheta: 3 frame median smoothed first derivative of the RightTheta, in degrees per frame.
* deriv1LeftTheta: 3 frame median smoothed first derivative of LeftTheta, in degrees per frame.
* rightdist: estimated linear distance  traveled in pixels by the tip of the right antenna between frames since the last moment calculated from the first derivative.
* leftdist: estimated linear distance traveled in pixels by the tip of the left antenna between frames since the last moment calculated from the first derivative.
* RightTheta.Mean.on.diff: Angle difference at this instance from the center for the right antenna compared to the mean for the right antenna across all odor windows, RightTheta.Mean.on.
* LeftTheta.Mean.on.diff: Angle difference at this instance from the center for the left antenna compared to the mean for the right antenna across all odor windows, LeftTheta.Mean.on.
* RightTheta.Mean.on: mean antennal angle from the center for the right antenna during odor presence.
* LeftTheta.Mean.on: mean antennal angle from the center for the left antenna during odor presence.
* RightTheta.Mean.off: mean antennal angle from the center for the right antenna prior to odor stimulation.
* LeftTheta.Mean.off:  mean antennal angle from the center for the left antenna prior to odor stimulation.
* iaa: the internal antenna angle, the angle between the two antennas at a given instance.
* odor_bin: binned odor time windows across the 90-second stimulus presentation and video recorded at 30 frames per second, approximately 2697 frames. Time was divided into 5 equal 18s bins, pre, bin1, bin2, bin3, bin 4.
* RightTheta.Mean.off.diff: Angle difference at this instance from the center for the right antenna compared to the mean for the right antenna across all pre-odor windows, RightTheta.Mean.off.
* LeftTheta.Mean.off.diff: Angle difference at this instance from the center for the left antenna compared to the mean for the right antenna across all pre-odor windows, LeftTheta.Mean.off.
* structure: the combinatorial factor for each plume structure and airflow speed.
* LeftTheta_trans: a 360-degree transformation of Left Theta, such that degrees fall between 0 and 180, rather than 181 to 360.
* LeftBI_dip: The binary variable of whether at this instance the left antenna is in forward or lateral position based upon the statistical dip test, with a boundary at 50 degrees. See the associated manuscript for additional details.
* RightBI_dip: The binary variable of whether at this instance the left antenna is in forward or lateral position based upon the statistical dip test, with a boundary at 50 degrees. See the associated manuscript for additional details.

## Code/software

None. Data was generated from raw videos using SwarmSight antennal tracking software, available at: [http://swarmsight.org/](http://swarmsight.org/).

## Access information

Other publicly accessible locations of the data:

* None

Data was derived from the following sources:

* Raw videos available upon request to Christopher M. Jernigan ([jernigc@wfu.edu](mailto:jernigc@wfu.edu)).
