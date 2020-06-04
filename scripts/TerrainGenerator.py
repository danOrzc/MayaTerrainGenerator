import maya.cmds as cmds
import maya.mel as mel
import math
import logging
from random import uniform as rand
from random import choice
from random import shuffle
import os
import colorsys

"""
    This tool creates a window that allows the user to create randomly generated terrains and add rocks to it.
    by Daniel Orozco
"""

# Creating a logger for debug
logger = logging.getLogger("TerrainGenerator")
logger.setLevel(logging.INFO)  # Allows us to see debug messages, change to INFO to hide

# Import timer in debug mode
if logger.level == logging.DEBUG:
    import time


class WindowCreator:
    """
    This is a class for creating and displaying UI elements that communicate with Terrain generator.
    Attributes:
        terrainName (str): The textField that receives the terrain's name.
        dimensionSlider (str): The slider for terrain's dimension.
        subdivisionSlider (str): The slider for terrain's subdivisions.
        methodField (str): The optionMenu to select the deformation method.
        valueDictionary (dict of {str:value}): The UI keys and the values they have.
        deformOptions (list of str): The possible deformation methods.
        terrainGenerator (TerrainGenerator): Object that manages how the terrain gets created.
    """

    # String that is used as a key to retrieve the window
    mainWindow = "terrain"

    def __init__(self):
        """
        The constructor of WindowCreator class
        """

        logger.debug("Initializing Window")

        # Setting attributes to identify UI elements
        self.terrainName = "terrainName"
        self.dimensionSlider = "dimensionSlider"
        self.subdivisionSlider = "subdivisionSlider"
        self.methodField = "methodField"
        self.terrainShaderName = "terrainShaderName"
        self.terrainColorIcon = "terrainColorIcon"
        self.terrainNormalIcon = "terrainNormalIcon"
        self.terrainSpecularIcon = "terrainSpecularIcon"

        self.rocksName = "rocksName"
        self.rockSlider = "rockSlider"
        self.rocksShaderName = "rocksShaderName"
        self.rocksColorIcon = "rocksColorIcon"
        self.rocksNormalIcon = "rocksNormalIcon"
        self.rocksSpecularIcon = "rocksSpecularIcon"
        self.colorSlider = "colorSlider"
        self.minBrightness = "minBrightness"
        self.maxBrightness = "maxBrightness"
        self.minSaturation = "minSaturation"
        self.maxSaturation = "maxSaturation"

        # Dictionary that uses UI elements as a key to store their values
        self.valueDictionary = {self.terrainName: "myTerrain",
                                self.dimensionSlider: 50,
                                self.subdivisionSlider: 50,
                                self.methodField: "Random Soft Select",
                                self.rocksName: "myRocks",
                                self.terrainShaderName: "terrain_mat",
                                self.terrainColorIcon: "",
                                self.terrainNormalIcon: "",
                                self.terrainSpecularIcon: "",
                                self.rockSlider: 1,
                                self.rocksShaderName: "rocks_mat",
                                self.rocksColorIcon: "",
                                self.rocksNormalIcon: "",
                                self.rocksSpecularIcon: "",
                                self.colorSlider: 120,
                                self.minBrightness: 0.0,
                                self.maxBrightness: 1.0,
                                self.minSaturation: 0.0,
                                self.maxSaturation: 1.0
                                }

        # Possible options to deform the terrain
        self.deformOptions = ["Random Soft Select", "Value Noise"]

        # Terrain generator object
        self.terrainGenerator = TerrainGenerator()

        self.windowWidth = 500

        # Call the function to start building the UI
        self.create_window()

    def create_window(self):
        """
        This function is the responsible for creating the window
        """

        # Close the window if it already exists
        if cmds.window(self.mainWindow, exists=True):
            cmds.deleteUI(self.mainWindow)

        # Create the window
        cmds.window(self.mainWindow, title="Terrain Generation",
                    w=self.windowWidth, sizeable=False)
        cmds.window(self.mainWindow, edit=True, w=self.windowWidth, h=320)

        # Call the function that creates the elements
        self.populate_window()

        # Display window
        cmds.showWindow(self.mainWindow)

    def populate_window(self):
        """
        This function creates the fields, sliders, etc contained in the window
        """

        tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

        '''
        ----------------------    Tab for Terrain Creation and its options ------------------------------------
        '''
        terrain_tab = cmds.columnLayout()

        # Main column layout inside the frame layout
        cmds.columnLayout(rowSpacing=2)

        self.make_separator(10)

        # Create the elements that will keep the general attributes for the terrain
        cmds.textFieldGrp(self.terrainName, label="Terrain Name", placeholderText="myTerrain",
                          changeCommand=
                          lambda new_val: self.update_value(new_val if new_val else "myTerrain", self.terrainName),
                          ann="The desired name for the terrain that is being created.")
        cmds.intSliderGrp(self.dimensionSlider, label="Terrain Dimension",
                          field=True, min=1, max=150, value=self.valueDictionary[self.dimensionSlider],
                          changeCommand=lambda new_val: self.update_value(new_val, self.dimensionSlider),
                          ann="Width and height sized for the terrain. This tool creates square terrains.")
        cmds.intSliderGrp(self.subdivisionSlider, label="Terrain Subdivisions",
                          field=True, min=1, max=150, value=self.valueDictionary[self.subdivisionSlider],
                          changeCommand=lambda new_val: self.update_value(new_val, self.subdivisionSlider),
                          ann="Amount of subdivisions of the new terrain. Uniform for width and height.")

        self.make_separator(10)

        # Column layout to center the optionMenu
        cmds.columnLayout(columnAttach=('both', self.windowWidth / 8), columnWidth=self.windowWidth)

        # Options for the user to choose terrain generation method
        cmds.optionMenu(self.methodField, label="Deformation Method",
                        changeCommand=lambda new_val: self.update_value(new_val, self.methodField),
                        ann="The method or algorithm used to deform the terrain.")
        cmds.menuItem(label="Random Soft Select",
                      annotation="Chooses random vertices with soft selection enabled and modifies their location")
        cmds.menuItem(label="Value Noise",
                      annotation="Calculates value noise using the coordinates of each vertex")

        cmds.setParent('..')  # Exit Menu column Layout

        # Texture section
        self.make_separator(10)
        cmds.textFieldGrp(self.terrainShaderName, label="Terrain material Name", placeholderText="terrain_mat",
                          changeCommand=
                          lambda new_val: self.update_value(new_val if new_val else "terrain_mat",
                                                            self.terrainShaderName),
                          ann="The desired name for the material applied to the terrain.")

        cmds.columnLayout(columnAttach=('both', self.windowWidth / 8), columnWidth=self.windowWidth)
        cmds.rowColumnLayout(numberOfColumns=3, rowSpacing=(1, 5),
                             columnWidth=[(1, self.windowWidth / 4),
                                          (2, self.windowWidth / 4),
                                          (3, self.windowWidth / 4)],
                             columnAttach=[(1, 'both', self.windowWidth / 8 - 50),
                                           (2, 'both', self.windowWidth / 8 - 50),
                                           (3, 'both', self.windowWidth / 8 - 50)])
        cmds.text(label="Color Map")
        cmds.text(label="Normal Map")
        cmds.text(label="Specular Map")
        cmds.iconTextButton(self.terrainColorIcon,
                            style='textOnly', w=100, h=100, bgc=(.2, .2, .2),
                            command=lambda: self.update_icon(self.terrainColorIcon),
                            ann="Texture used as Color Map in the material")
        cmds.iconTextButton(self.terrainNormalIcon,
                            style='textOnly', w=100, h=100, bgc=(.2, .2, .2),
                            command=lambda: self.update_icon(self.terrainNormalIcon),
                            ann="Texture used as Normal Map in the material")
        cmds.iconTextButton(self.terrainSpecularIcon,
                            style='textOnly', w=100, h=100, bgc=(.2, .2, .2),
                            command=lambda: self.update_icon(self.terrainSpecularIcon),
                            ann="Texture used as Specular Map in the material")
        cmds.setParent('..')  # Exit Row Layout
        cmds.setParent('..')  # Exit Centered column layout

        # Execute Creation buttons
        self.make_separator(10)
        cmds.columnLayout(columnAttach=('both', self.windowWidth/8), columnWidth=self.windowWidth)
        cmds.rowLayout(numberOfColumns=2, columnWidth2=[self.windowWidth/2, self.windowWidth/2])
        cmds.button(label="Create new terrain", width=self.windowWidth/4, command=self.create_and_deform,
                    ann="Creates a new terrain using the selected deformation method.")
        cmds.button(label="Add deformation", width=self.windowWidth/4, command=self.just_deform,
                    ann="Adds another layer of deformation to the PREVIOUSLY created terrain with the selected method.")
        cmds.setParent('..')  # Exit Row Layout
        cmds.setParent('..')  # Exit Centered column layout

        cmds.setParent('..')  # Exit MAIN column layout
        cmds.setParent('..')  # Exit Frame Layout

        '''
        ----------------------------    Tab for Rock Creation and its options  --------------------------------
        '''
        rocks_tab = cmds.columnLayout()

        # Main column layout for rocks
        cmds.columnLayout(rowSpacing=2)
        self.make_separator(10)

        cmds.textFieldGrp(self.rocksName, label="Rocks Name", placeholderText="myRocks",
                          changeCommand=
                          lambda new_val: self.update_value(new_val if new_val else "myRocks", self.rocksName),
                          ann="Common name shared within all the rocks created. This tool groups the rocks inside a "
                              "group with the same name with _grp suffix")
        cmds.intSliderGrp(self.rockSlider, label="Rocks Amount",
                          field=True, min=1, max=100, value=self.valueDictionary[self.rockSlider],
                          changeCommand=lambda new_val: self.update_value(new_val, self.rockSlider),
                          ann="The amount of rocks generated")

        # Texture section
        self.make_separator(10)
        cmds.textFieldGrp(self.rocksShaderName, label="Rocks material Name", placeholderText="rocks_mat",
                          changeCommand=
                          lambda new_val: self.update_value(new_val if new_val else "rocks_mat",
                                                            self.rocksShaderName),
                          ann="The desired name for the material applied to the terrain.")
        cmds.columnLayout(columnAttach=('both', self.windowWidth / 8), columnWidth=self.windowWidth)
        cmds.rowColumnLayout(numberOfColumns=2, rowSpacing=(1, 5),
                             columnWidth=[(1, 3 * self.windowWidth / 8),
                                          (2, 3 * self.windowWidth / 8)],
                             columnAttach=[(1, 'both', 3 * self.windowWidth / 16 - 50),
                                           (2, 'both', 3 * self.windowWidth / 16 - 50)])
        cmds.text(label="Color Map")
        cmds.text(label="Normal Map")
        cmds.iconTextButton(self.rocksColorIcon,
                            style='textOnly', w=100, h=100, bgc=(.2, .2, .2),
                            command=lambda: self.update_icon(self.rocksColorIcon),
                            ann="Texture used as Color Map in the material")
        cmds.iconTextButton(self.rocksNormalIcon,
                            style='textOnly', w=100, h=100, bgc=(.2, .2, .2),
                            command=lambda: self.update_icon(self.rocksNormalIcon),
                            ann="Texture used as Normal Map in the material")
        cmds.setParent('..')  # Exit Row Layout

        self.make_separator(10)

        # Section for Ambient Color
        cmds.text(label="Ambient Color")
        cmds.separator(height=10, style="none")

        cmds.intSliderGrp(self.colorSlider, value=120, min=0, max=359,
                          dc=lambda new_val: self.update_color(new_val, self.colorSlider))
        cmds.canvas("colorDisplay", backgroundColor=(0, 1, 0), w=50, h=50)

        cmds.separator(height=10, style="none")
        cmds.rowColumnLayout(numberOfColumns=2, rowSpacing=(1, 5),
                             columnWidth=[(1, 3 * self.windowWidth / 8),
                                          (2, 3 * self.windowWidth / 8)],
                             columnAttach=[(1, 'both', 3 * self.windowWidth / 16 - 50),
                                           (2, 'both', 3 * self.windowWidth / 16 - 50)])
        cmds.text(label="Min Saturation:")
        cmds.text(label="Max Saturation:")
        cmds.floatField(self.minSaturation, max=1.0, min=0.0,
                        changeCommand=lambda new_val: self.update_value(new_val, self.minSaturation),
                        ann="Minimum saturation used by the ambient color attribute."
                            "Make both values ZERO to use grayscale")
        cmds.floatField(self.maxSaturation, value=1, max=1.0, min=0.0,
                        changeCommand=lambda new_val: self.update_value(new_val, self.maxSaturation),
                        ann="Maximum saturation used by the ambient color attribute"
                            "Make both values ZERO to use grayscal")
        cmds.setParent('..')  # Exit Row Layout

        cmds.separator(height=10, style="none")
        cmds.rowColumnLayout(numberOfColumns=2, rowSpacing=(1, 5),
                             columnWidth=[(1, 3 * self.windowWidth / 8),
                                          (2, 3 * self.windowWidth / 8)],
                             columnAttach=[(1, 'both', 3 * self.windowWidth / 16 - 50),
                                           (2, 'both', 3 * self.windowWidth / 16 - 50)])
        cmds.text(label="Min Brightness:")
        cmds.text(label="Max Brightness:")
        cmds.floatField(self.minBrightness, max=1.0, min=0.0,
                        changeCommand=lambda new_val: self.update_value(new_val, self.minBrightness),
                        ann="Minimum brightness used by the ambient color attribute")
        cmds.floatField(self.maxBrightness, value=1, max=1.0, min=0.0,
                        changeCommand=lambda new_val: self.update_value(new_val, self.maxBrightness),
                        ann="Maximum brightness used by the ambient color attribute")
        cmds.setParent('..')  # Exit Row Layout

        cmds.setParent('..')  # Exit Centered column layout

        # Execution
        self.make_separator(10)
        # Button column layout
        cmds.columnLayout(columnAttach=('both', self.windowWidth / 8), columnWidth=self.windowWidth)
        cmds.button(label="Create Rocks", align='right', width=self.windowWidth/4, command=self.create_rocks,
                    ann="Spawns the selected amount of rocks on the terrain's surface.")
        cmds.setParent('..')  # Exit Button Column Layout

        self.make_separator(10)

        cmds.setParent('..')  # Exit Main column Layout
        cmds.setParent('..')  # Exit Frame Layout

        '''
        ----------------------------------------------------------------------------------------------------------------
        '''
        cmds.tabLayout(tabs, edit=True, tabLabel=((terrain_tab, 'Terrain'), (rocks_tab, 'Rocks')))

        '''
        ------------------------------------ Development Tools ---------------------------------------------------------
        '''
        if logger.level == logging.DEBUG:
            cmds.frameLayout(label="Development Tools", bgc=(.5, 0, 0))
            cmds.gridLayout(nc=3, cellWidthHeight=(self.windowWidth / 3, 20))
            cmds.button(label="Delete Unused Nodes", w=self.windowWidth / 3,
                        command=lambda x: mel.eval('MLdeleteUnused;'))
            cmds.button(label="Delete All Objects", w=self.windowWidth / 3,
                        command=lambda x: cmds.delete(cmds.ls(dag=True)))

    def delete_unused(self, *args):
        mel.eval('MLdeleteUnused;')

    def create_and_deform(self, *args):
        """
        This function creates a terrain and deforms it using the Generator object
        Parameters:
            *args (list): Used to keep the information sent by the UI elements
        """
        logger.debug("Create NEW Terrain")
        # Execute function for terrain creation
        self.terrainGenerator.create_terrain(
            grid_name=self.valueDictionary[self.terrainName],
            dimensions=self.valueDictionary[self.dimensionSlider],
            subdivisions=self.valueDictionary[self.subdivisionSlider])

        # Execute deformation
        deformation_index = self.deformOptions.index(self.valueDictionary[self.methodField])

        self.terrainGenerator.deform_terrain(deformation_index)

        # Assign material
        material = create_material(self.valueDictionary[self.terrainShaderName],
                                   self.valueDictionary[self.terrainColorIcon],
                                   self.valueDictionary[self.terrainNormalIcon],
                                   self.valueDictionary[self.terrainSpecularIcon])

        cmds.select(self.terrainGenerator.gridObject)
        cmds.hyperShade(assign=material)

    def just_deform(self, *args):
        """
        This function modifies an existing terrain using the Generator object
        Parameters:
            *args (list): Used to keep the information sent by the UI elements
        """
        logger.debug("Just deform Terrain")

        # Execute deformation
        deformation_index = self.deformOptions.index(self.valueDictionary[self.methodField])

        self.terrainGenerator.deform_terrain(deformation_index)

    def create_rocks(self, *args):
        """
        This function creates random rocks using the Generator object
        Parameters:
            *args (list): Used to keep the information sent by the UI elements
        """
        logger.debug("Bring the rocks!")

        self.terrainGenerator.create_rocks(self.valueDictionary[self.rocksName],
                                           self.valueDictionary[self.rockSlider],
                                           self.valueDictionary[self.rocksShaderName],
                                           self.valueDictionary[self.rocksColorIcon],
                                           self.valueDictionary[self.rocksNormalIcon],
                                           self.valueDictionary[self.colorSlider],
                                           (self.valueDictionary[self.minBrightness],
                                            self.valueDictionary[self.maxBrightness]),
                                           (self.valueDictionary[self.minSaturation],
                                            self.valueDictionary[self.maxSaturation])
                                           )

    def update_color(self, hue, color_slider):
        logger.debug("Hue is: {}".format(hue))

        rgb = colorsys.hsv_to_rgb(hue/360.0, 1.0, 1.0)

        logger.debug("RGB is: {}".format(rgb))

        cmds.button("colorDisplay", edit=True, backgroundColor=rgb)

        self.update_value(hue, color_slider)

    def update_icon(self, icon):
        """
        This function receives the name of an icon and updates its image with a selected file.
        Parameters:
            icon (str): The name that is used to reference the icon
        """
        map_name = icon
        map_name = map_name[map_name.find("terrain")+len("terrain"):map_name.rfind("Icon")]
        filename = cmds.fileDialog2(fileMode=1, caption="Import {} Map".format(map_name))

        if filename:
            the_file = filename and os.path.normpath(filename[0])
            cmds.iconTextButton(icon, e=True, style="iconOnly")
            cmds.iconTextButton(icon, e=True, image=the_file)
        else:
            the_file = ""
            cmds.iconTextButton(icon, e=True, style="textOnly")

        self.update_value(the_file, icon)

    def update_value(self, *args):
        """
        This function creates a terrain and deforms it using the Generator object
        Parameters:
            *args (list): Used to keep the information sent by the UI elements.
                          First index saves the value; Second index saves UI's key to access the value.
        """
        logger.debug("Value has changed")
        logger.debug("Updating value from: " + str(args[1]))

        # Change value that is connected to this key
        self.valueDictionary[args[1]] = args[0]

        logger.debug("New value is: " + str(self.valueDictionary[args[1]]))

    def make_separator(self, height):
        """
        This function creates an UI separator
        Parameters:
            height (int): The height in pixels for this separator
        """
        cmds.separator(height=height)


class TerrainGenerator:
    """
    This is a class for creating and displaying UI elements that communicate with Terrain generator.
        Attributes:
            gridObject (str): Reference to the grid used to generate the terrain.
            gridDimensions (int): Width and height of the grid.
            gridSubdivisions (int): Quantity of subdivisions uses by the grid.
            maxHeight (float): Max amount of movement in Y axis possible for a vertex.
            maxPoints (int): Max number of vertices that can be used in softSelection method.
            softSelectRadius (float): Max radius that is used by the softSelectTool.
            curves (list of str): Falloff curves used by the softSelectTool.
            noise_seed (int): Seed used for generating noise
            rocksName (str): The name used for the creating rocks and their group
            rocksAmount (int): The number of rocks that are going to be generated.
            sphereStartRadius (float): The starting point for generating rocks.
    """

    def __init__(self):
        """
        The constructor of TerrainGenerator class
        """
        # Terrain attributes
        self.gridObject = ""
        self.gridDimensions = 10
        self.gridSubdivisions = 10

        # Maximum modification values, these were obtained by trial with a 100x100 grid.
        self.maxHeight = 7.5
        self.maxPoints = 100

        # Attributes for Soft Selection
        self.softSelectRadius = 20.0
        self.curves = ["1,0,2,0,1,2", "1,0.5,2,0,1,2,1,0,2", "1,0.05,3,0,1,3,0.5,0.4,3"]

        # Attributes for value noise
        self.noise_seed = 6000

        # Attributes for rock creation
        self.rocksName = ""
        self.rocksAmount = 1
        self.sphereStartRadius = .8

    def create_terrain(self, grid_name, dimensions, subdivisions):
        """
        This function creates the grid with parameters given.
            Parameters:
                grid_name (str): The name that the terrain is going to have.
                dimensions (int): Dimensions for width and height.
                subdivisions (int): Amount of subdivisions for the grid.
        """
        if logger.level == logging.DEBUG:
            start_time = time.time()

        # Create polyPlane with given parameters
        cmds.polyPlane(name=grid_name, width=dimensions, height=dimensions,
                       sx=subdivisions, sy=subdivisions)

        # Save those values so they can be accessed by other functions
        self.gridObject = cmds.ls(selection=True)[0]
        self.gridDimensions = dimensions
        self.gridSubdivisions = subdivisions

        if logger.level == logging.DEBUG:
            logger.debug("--- Grid CREATION took: {} ---".format(time.time() - start_time))

    def deform_terrain(self, deformation_method):
        """
        This function deforms the terrain previously created.
            Parameters:
                deformation_method (int): The desired method to deform the grid.
        """
        if logger.level == logging.DEBUG:
            start_time = time.time()

        # Select deformation based on the value entered
        if deformation_method == 0:
            self.soft_random()
        elif deformation_method == 1:
            self.value_noise()

        if logger.level == logging.DEBUG:
            logger.debug("--- Grid DEFORMATION took: {} ---".format(time.time() - start_time))

    def modify_terrain(self, deformation_method):
        """
        This function deletes previous terrain and creates another one with same parameters.
            Parameters:
                deformation_method (int): The desired method to deform the grid.
        """
        cmds.delete(self.gridObject)

        cmds.polyPlane(name=self.gridObject, width=self.gridDimensions, height=self.gridDimensions,
                       sx=self.gridSubdivisions, sy=self.gridSubdivisions)

        self.deform_terrain(deformation_method)

    def soft_random(self):
        """
        This function modifies the grid by using Soft Selection
        """
        logger.debug("Starting deformation with soft selection")

        if not self.check_terrain():
            return

        # Multipliers to scale deformation according to the selected size.
        radius_multiplier = self.gridDimensions/100.0
        height_multiplier = self.gridDimensions/100.0
        points_multiplier = self.gridSubdivisions/100.0

        # Scale the limit of the height to modify it after randomizing
        height_limit = self.maxHeight*height_multiplier/2.0

        # List of every vertex on the object
        vertices = cmds.ls(self.gridObject + ".vtx[*]", flatten=True)

        # Number of vertices that are going to be modified.
        # We add 2 to at least modify 2 vertices
        vertices_to_edit = int(self.maxPoints * points_multiplier + 2)

        logger.debug("About to edit: {} vertices".format(vertices_to_edit))

        # Number of sections to divide the terrain
        # These sections are used to better distribute the deformed vertices
        # If there are not enough vertices, use all of them individually
        section_amount = 8 if vertices_to_edit >= 8 else vertices_to_edit

        # The size that each section should have
        section_size = len(vertices)/section_amount

        # Create a list from index i until the section is full
        # Do that from index 0 in vertices to the end of the list,
        # skipping the number of elements of the section
        vertex_sections = [vertices[i:i + section_size]
                           for i in range(0, len(vertices), section_size)]

        # Fill a list with numbers from 0 to the number of sections in that the grid is divided
        grid_indexes = [i for i in range(0, section_amount)]

        # Shuffle that so the grids are chosen in a random order
        shuffle(grid_indexes)

        # Loop with through a set number of vertices
        for v in range(vertices_to_edit):
            # Enable soft selection to move smoothly
            cmds.softSelect(sse=True,
                            ssd=self.softSelectRadius*radius_multiplier,
                            ssc=choice(self.curves))

            # Select a random vertex on the grid
            grid_index = v % section_amount

            cmds.select(choice(vertex_sections[grid_indexes[grid_index]]))

            # Randomize movement on that vertex
            random_y = rand(-height_limit, height_limit)

            # Add variation so the range doesn't start in 0
            random_y = random_y + height_limit if random_y >= 0 else random_y - height_limit

            # Apply movement
            cmds.move(0, random_y, 0, r=True)

        # Disable softSelection to avoid errors in other functions
        cmds.softSelect(sse=False)

        # Soften edges
        cmds.polySoftEdge(self.gridObject, a=180, ch=1)

    def value_noise(self):
        """
        This function modifies the grid by using an implementation of value Noise
        """
        logger.debug("Starting deformation with value noise")

        if not self.check_terrain():
            return

        # Disable softSelection to avoid errors in other functions
        cmds.softSelect(sse=False)

        self.noise_seed = rand(0, 1)*10000

        logger.debug("Random seed is: {}".format(self.noise_seed))

        # List of every vertex on the object
        vertices = cmds.ls(self.gridObject + ".vtx[*]", flatten=True)

        # Multiplier to scale deformation according to the selected size.
        height_multiplier = self.gridDimensions / 100.0

        # Set the max Y value for the points.
        # Multiply by 3 because this generates smaller values than soft selection
        height_limit = self.maxHeight * height_multiplier * 3.0

        # Nested for loops to get "coordinates" of each vertex
        for x in range(0, self.gridSubdivisions + 1):
            for y in range(0, self.gridSubdivisions + 1):

                # Normalize x and y coordinates to fit range 0-1
                normalized_x = x*1.0 / self.gridSubdivisions
                normalized_y = y*1.0 / self.gridSubdivisions

                # Store evaluated noise from each coordinate multiplied by a scale
                # Add octaves together and return to 0 to 1 range
                value = smooth_noise(normalized_x * 4.0, normalized_y * 4.0, self.noise_seed)
                value += smooth_noise(normalized_x * 8.0, normalized_y * 8.0, self.noise_seed) * .5
                value += smooth_noise(normalized_x * 16.0, normalized_y * 16.0, self.noise_seed) * .25
                value += smooth_noise(normalized_x * 32.0, normalized_y * 32.0, self.noise_seed) * .125
                value /= (1 + .5 + .25 + .125)

                # Calculate vertex index on the object using x and y
                index = x * (self.gridSubdivisions+1) + y

                # Move the vertex on Y with the noise value
                cmds.move(0, value * height_limit, 0, vertices[index], r=True)

    def create_rocks(self, rocks_name, rocks_amount, mat_name, color, normal, hue, brightness_range, saturation_range):
        """
        This function creates certain amount of rocks with a set name
            Parameters:
                rocks_name: The name that rocks will have
                rocks_amount: The amount of rocks that are going to be generated
                mat_name: The name for Rocks' Blinn
                color: Color map used by the Blinn
                normal: Normal map used
                hue: The hue selected for the rocks to use in the ambient color
                brightness_range: range given by the user to set the ambient color

        """
        if logger.level == logging.DEBUG:
            start_time = time.time()

        # Disable softSelection to avoid errors in other functions
        cmds.softSelect(sse=False)

        # Get a percentage of the size compared to original rock
        size_multiplier = self.gridDimensions/100.0

        # Assign a group name based on the name selected
        rocks_group = rocks_name + "_grp"

        # Variable used in for loop to check if there is an existing terrain
        terrain_verification = 1

        # Assign material
        material = create_material(mat_name, color, normal)
        switch_node = cmds.shadingNode("tripleShadingSwitch", asUtility=True)
        cmds.connectAttr("%s.output" % switch_node, "%s.ambientColor" % material)

        # Rock creation
        for i in range(rocks_amount):
            # Set new radius using the multiplier
            sphere_radius = self.sphereStartRadius*size_multiplier

            # Create sphere as base for rocks
            new_sphere = cmds.polySphere(name=rocks_name, radius=sphere_radius,
                                         subdivisionsAxis=20, subdivisionsHeight=20)

            # Deform newly created sphere
            self.deform_rock(new_sphere[0], sphere_radius)

            # Disable softSelection to avoid errors in other functions
            cmds.softSelect(sse=False)

            # Select sphere again
            cmds.select(new_sphere)

            # Variations to scale
            random_scale_x = rand(.2, 1)
            random_scale_y = random_scale_x + rand(-.1, .1)  # Small variations on other axes
            random_scale_z = random_scale_x + rand(-.1, .1)  # Small variations on other axes

            # Scale using variables
            cmds.scale(random_scale_x, random_scale_y, random_scale_z)

            # Freeze transformations
            cmds.makeIdentity(apply=True)

            # Random numbers locations based on terrain size
            random_position_x = rand(-self.gridDimensions / 2, self.gridDimensions / 2)
            random_position_z = rand(-self.gridDimensions / 2, self.gridDimensions / 2)

            # Move sphere inside range defined by terrain
            cmds.move(random_position_x, 0, random_position_z)

            # Try to snap rocks to terrain only if there is a terrain
            if terrain_verification > 0:
                try:
                    # Select actual terrain
                    cmds.select(self.gridObject, new_sphere)

                    # Constraint to Terrain's Geometry
                    cmds.geometryConstraint(weight=True)

                    # Constraint to Terrain's normals to make rocks point the right direction
                    cmds.normalConstraint(weight=True, aimVector=(0, 1, 0), upVector=(1, 0, 0), worldUpType=0)

                    # Delete constraints
                    cmds.delete(cmds.listRelatives(new_sphere, children=True)[1:])

                except ValueError:
                    logger.warn("No terrain was previously created, or got deleted. Spawning rocks randomly...")
                    terrain_verification -= 1

            # Try to select the group, if its not possible, then create it
            try:
                cmds.select(new_sphere, rocks_group)
            except ValueError:
                cmds.group(name=rocks_group, empty=True)
                cmds.select(new_sphere, rocks_group)

            # Parent rocks to group and save rock's new name
            actual_rock = cmds.parent()

            # Connect shape to switch Node
            sphere_shape = cmds.listRelatives(actual_rock[0], shapes=True)[0]
            cmds.connectAttr("%s.instObjGroups[0]" % sphere_shape, "%s.input[%i].inShape" % (switch_node, i))

            # Create color nodes
            random_brightness = rand(brightness_range[0], brightness_range[1])
            random_saturation = rand(saturation_range[0], saturation_range[1])
            color = colorsys.hsv_to_rgb(hue/360.0, random_saturation, random_brightness*1.0)
            logger.debug("HUE is {}".format(hue))
            logger.debug("Rock is having {} color".format(color))
            color_node = cmds.shadingNode("colorConstant", asUtility=True)
            cmds.setAttr("%s.inColor" % color_node, color[0], color[1], color[2], type="double3")
            cmds.connectAttr("%s.outColor" % color_node, "%s.input[%i].inTriple" % (switch_node, i))

            # Assign material to rock
            cmds.select(actual_rock)
            cmds.hyperShade(assign=material)

        if logger.level == logging.DEBUG:
            logger.debug("--- ROCK CREATION took: {} ---".format(time.time() - start_time))

    def deform_rock(self, sphere, radius):
        """
        This function takes a sphere with its radius and deforms it.
            Parameters:
                sphere (str): The sphere that is going to be modified.
                radius (float): The radius of the sphere.
        """
        logger.debug("Deforming a rock: {}".format(sphere))

        # Random radius used for soft selection
        soft_select_radius = rand(-.1, .1) * radius

        # Smooth curve used for selection
        rock_falloff = "1,0,2,0,1,2"

        # Move random range far from 0
        # If radius was greater than 0, add 1. Else substract 1
        soft_select_radius = (soft_select_radius + 1 * radius) \
            if soft_select_radius >= 0 \
            else (soft_select_radius - 1 * radius)

        # List of every vertex on the object
        vertices = cmds.ls(sphere + ".vtx[*]", flatten=True)

        # Enable soft selection with generated radius
        cmds.softSelect(sse=True,
                        ssd=3*abs(soft_select_radius),
                        ssc=rock_falloff)

        # Select and scale base of sphere to create planar base
        cmds.select(vertices[-2])
        cmds.scale(1, .00005*radius, 1, pivot=(0, -1*radius, 0), r=True)

        # Change selection radius
        cmds.softSelect(sse=True,
                        ssd=1.5*abs(soft_select_radius),
                        ssc=rock_falloff)

        # Select and move a vertex in the middle of the sphere
        cmds.select(vertices[len(vertices)/2])
        cmds.move(0.8*radius, 0, 0, r=True, cs=True, ls=True, wd=True)

        # Select and move the top of the sphere
        cmds.select(vertices[-1])
        cmds.move(0.4*radius, 0, 0, r=True, cs=True, ls=True, wd=True)

        # Disable softSelection to avoid errors in other functions
        cmds.softSelect(sse=False)

        # Move pivot down to base of the sphere
        cmds.move(0, -.95*radius, 0, sphere + ".scalePivot", r=True)
        cmds.move(0, -.95*radius, 0, sphere + ".rotatePivot", r=True)

    def check_terrain(self):
        # Check if object exists, if it doesn't give warning to user
        try:
            if not self.gridObject:
                logger.error("No terrain was previously created, or got deleted. Please create one before deforming.")
                return False
            cmds.select(self.gridObject)
        except ValueError:
            logger.error("No terrain was previously created, or got deleted. Please create one before deforming.")
            return False

        return True


def create_material(name="myBlinn", color="", normal="", specular=""):

    # Create blinn Node
    my_shader = cmds.shadingNode("blinn", asShader=True)
    my_shader = cmds.rename(my_shader, name)

    logger.debug("The Color is: {}".format(color))

    if color:
        # Creating baseColor Node
        file_node = cmds.shadingNode("file", asTexture=True)
        filename = color
        cmds.setAttr("%s.fileTextureName" % file_node, filename, type="string")  # Connect file to node
        # Connect attributes to Blinn
        cmds.connectAttr("%s.outColor" % file_node, "%s.color" % my_shader)

    if normal:
        # Creating file Node for normal Map
        normal_node = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
        cmds.setAttr("%s.ignoreColorSpaceFileRules" % normal_node, 1)
        filename = normal
        cmds.setAttr("%s.fileTextureName" % normal_node, filename, type="string")  # Connect file to node
        cmds.setAttr("%s.colorSpace" % normal_node, "Raw", type="string")
        bump_node = cmds.shadingNode("bump2d", asUtility=True)
        cmds.connectAttr("%s.outAlpha" % normal_node, "%s.bumpValue" % bump_node)  # Connect file to bump
        cmds.setAttr("%s.bumpInterp" % bump_node, 1)  # Set to tangent space normals
        # Connect attributes to Blinn
        cmds.connectAttr("%s.outNormal" % bump_node, "%s.normalCamera" % my_shader)

    if specular:
        # Creating Nodes for specular
        spec_node = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
        cmds.setAttr("%s.ignoreColorSpaceFileRules" % spec_node, 1)
        filename = specular
        cmds.setAttr("%s.fileTextureName" % spec_node, filename, type="string")  # Connect file to node
        cmds.setAttr("%s.colorSpace" % spec_node, "Raw", type="string")
        # Connect attributes to Blinn
        cmds.connectAttr("%s.outColor" % spec_node, "%s.specularColor" % my_shader)

    # Change ambient color attribute
    cmds.setAttr("{}.ambientColor".format(my_shader), 0, 0, 0, type="double3")

    return my_shader


def smooth_noise(point_x, point_y, random_seed=6000):
    """
    This function modifies the grid by using an implementation of value Noise.
    Utilizes sine-based noise for each point and interpolates values from adjacent points.
        Parameters:
            point_x (float): X coordinate of a point
            point_y (float): Y coordinate of a point
            random_seed (float): seed used to generate the values. Default to 6000
        Returns:
            interpolation (float): The noise value obtained for specified coordinates
    """
    # Getting decimal part of the local grids defined by the octaves to use for smooth step
    # Gets numbers from 0 to 1 that repeat depending on scale used
    local_coordinate_x = math.modf(point_x)[0]
    local_coordinate_y = math.modf(point_y)[0]

    # Smooth step for local grids
    smooth_local_x = (local_coordinate_x**2)*(3-(2*local_coordinate_x))
    smooth_local_y = (local_coordinate_y**2)*(3-(2*local_coordinate_y))

    # Getting the grid ID with integer part.
    # Get values from 0 to 4, 0 to 8, 0 to 16... depends on scale used
    grid_id_x = math.modf(point_x)[1]
    grid_id_y = math.modf(point_y)[1]

    # Evaluate grid locations with the noise function and interpolate both corners
    bottom_left = noise_from_coordinates(grid_id_x, grid_id_y, random_seed)
    bottom_right = noise_from_coordinates(grid_id_x + 1, grid_id_y, random_seed)
    bottom = linear_interpolation(bottom_left, bottom_right, smooth_local_x)

    # Evaluate grid locations with the noise function and interpolate both corners
    top_left = noise_from_coordinates(grid_id_x, grid_id_y + 1, random_seed)
    top_right = noise_from_coordinates(grid_id_x + 1, grid_id_y + 1, random_seed)
    top = linear_interpolation(top_left, top_right, smooth_local_x)

    # Calculate interpolation based on opposite corners using Y smooth step
    interpolation = linear_interpolation(bottom, top, smooth_local_y)

    return interpolation


def noise_from_coordinates(point_x, point_y, random_seed=6000):
    """
    This function modifies obtains a simple noise based on sine for a given point
        Parameters:
            point_x (float): X coordinate of a point
            point_y (float): Y coordinate of a point
            random_seed (float): seed used to generate the values. Default to 6000
        Returns:
            random_value (float): The value obtained for specified coordinates
    """
    # Get random Y from sine curve
    random_value = math.sin(point_x*100 + point_y*random_seed)*random_seed

    # Get only the decimal part to make it go from 0 to 1
    random_value = math.modf(random_value)[0]

    # Return random Y value
    return random_value


def linear_interpolation(first_value, second_value, alpha):
    return first_value * (1 - alpha) + second_value * alpha


def cosine_interpolation(first_value, second_value, alpha):
    interpolation = (1 - math.cos(alpha*math.pi))/2.0
    return first_value * (1 - interpolation) + second_value * interpolation


terrainGen = WindowCreator()
