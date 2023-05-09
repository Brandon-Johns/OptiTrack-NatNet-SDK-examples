# How to get an indoor MoCap system to function outdoors
If you have a system designed for outdoors, by all means, but if you just gotta make it work with a regular MoCap system, then here's some tips based off my struggles. I did get it working!

OptiTrack can function outdoors, even in the full summer sun! Expect less than half the operational range outdoors as compared to indoors.

## First consider how OptiTrack functions
1. Emission
	- The LED rings around the camera lens emit near-infrared (IR) light
2. Refection
	- The emitted light that hits the makers reflects directly back at the camera lens due to use of [corner reflectors](https://en.wikipedia.org/wiki/Corner_reflector)
	- The light that hits the rest of the environment mostly reflects or scatters in other directions, as the occurrence of corner reflectors that happen to be highly reflective in IR is not common in everyday environments
3. Detection
	- The cameras take a photo of the scene in the IR spectrum
	- The light that reflected off the markers directly back at the camera lens will cause bright dots, while the rest of the scene will hopefully be dim in IR
	- Other sources of bright detections are
		- A camera directly seeing the emitter of another camera
		- The light from one camera reflects off a polished object by [specular reflection](https://en.wikipedia.org/wiki/Specular_reflection) (as opposed to [diffuse reflection](https://en.wikipedia.org/wiki/Diffuse_reflection) off rough objects). This light may reflect back at the same camera or into a different camera as per the angle of incidence of the light onto the surface
	- Motive analyses the IR image for bright circular dots and labels them as markers
	- Allowing any other bright sources in the image should therefore be avoided by removing reflective surfaces, pixel masking, etc.

## How working outdoors can impact the normal functioning
1. Emission
	- The sun also outputs IR light. On a sunny day, the emission is much stronger than the LEDs on the cameras. Hence, the sun should also be treated as an emitter
2. Refection
	- Location dependent, you may be in the presence of many surfaces that are highly reflective in IR and pointing in a large variety of directions that the sunlight will be well reflected in mostly every direction (e.g. grass)
3. Detection
	- As the IR light source is much stronger, the sensors will receive more light
	- The makers still need to be distinguishable from other reflections in the scene

## How to get OptiTrack working outdoors
1. Setup the hardware and start Motive
	- Don't face the cameras towards the sun. Angled down is preferable
2. For each camera
	1. In Motive, right-click the camera view and change the view to `Raw Greyscale`. This shows exactly what the camera is seeing in IR. The goal from here is to make the scene dark grey, with only the markers appearing bright
	2. Place markers in the scene
	3. Reduce the camera exposure `(EXP)` as far as possible while the markers still appear bright. I reduced to `30`
	4. Keep the other camera settings as is (e.g. LED at maximum)
	5. Identify any objects that appear as bright as the markers and cover them with non-reflective material, or if a marker will never appear in that location, then mask the pixel
		- You can combine pressing the auto-mask button multiple times with manually drawings masks if the background reflections are moving (e.g. grass)
3. That's all, really
4. And grass is the worst, really

## Materials for covering the background
The stronger the sun, the better material you need to find to absorb the IR light. Thankfully you can test your materials by simply placing them in front of the camera in `Raw Greyscale` mode and seeing how bright they appear.

- **Best Weather**
	- In the shade
	- On cloudy days
- **Best materials**
	- Whatever the magic paint they used on the wand and the origin square
	- EVA foam (e.g. [from Bunnings](https://www.bunnings.com.au/eva-50-x-50cm-interlock-foam-mats-solid-black-pk4_p0126584))
	- Black PLA (e.g. 3D printed objects).
	- Black painted wood boards
	- Asphalt
- **Moderate materials**
	- Masking tape
	- Concrete
- **Bad materials**
	- White PLA (e.g. 3D printed objects).
	- Most fabrics (yes, even black fabric)
	- Unpainted metal
	- Grass
