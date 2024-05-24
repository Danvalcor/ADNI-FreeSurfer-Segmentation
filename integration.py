import os
import vtk
import numpy as np
import pandas as pd
import tkinter as tk
import nibabel as nib
import matplotlib.pyplot as plt
from helperFuns import *
from nilearn import image
from skimage import measure
from nilearn import plotting, image
from tkinter import filedialog, ttk
from matplotlib.colors import ListedColormap
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from vtkmodules.util.numpy_support import numpy_to_vtk
from vtkmodules.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor
from vtkmodules.tk.vtkTkRenderWidget import vtkTkRenderWidget


class App:
    def __init__(self, root):
        # MRI data
        self.img = None
        self.brain = None
        self.segment = None
        self.segmentsDF = None
        self.lut = loadLUT()
        
        # Promgrams root.
        self.root = root
        self.root.title("ANDI - Freesurfer")
        
        # Left frame for menu
        self.leftFrame = tk.Frame(root)
        self.leftFrame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Folder selection button
        self.folderVar = tk.StringVar()
        self.folderButton = tk.Button(self.leftFrame, text="Seleccionar Carpeta", command=self.selectFolder)
        self.folderButton.pack(anchor='w', pady=5)
        
        # Selected folder label
        self.folderLabel = tk.Label(self.leftFrame, text="Carpeta seleccionada: Ninguna")
        self.folderLabel.pack(anchor='w', pady=5)
        
        # Frame for the buttons
        self.buttonsIndicatorsFrame = tk.Frame(self.leftFrame)
        self.buttonsIndicatorsFrame.pack(anchor='w', pady=10)
        
        # Buttons and their indicators 
        self.visualizeButton = tk.Button(self.buttonsIndicatorsFrame, text="visualize", command=self.visualize, state=tk.DISABLED)
        self.visualizeButton.grid(row=0, column=0, sticky='w', pady=5)
        
        self.visualizeIndicator = tk.Canvas(self.buttonsIndicatorsFrame, width=20, height=20)
        self.visualizeIndicator.create_oval(2, 2, 18, 18, fill="red")
        self.visualizeIndicator.grid(row=0, column=1, padx=10)
        
        self.segmentar_button = tk.Button(self.buttonsIndicatorsFrame, text="Segmentar", command=self.segmentar, state=tk.DISABLED)
        self.segmentar_button.grid(row=1, column=0, sticky='w', pady=5)
        
        self.segmentar_indicator = tk.Canvas(self.buttonsIndicatorsFrame, width=20, height=20)
        self.segmentar_indicator.create_oval(2, 2, 18, 18, fill="red")
        self.segmentar_indicator.grid(row=1, column=1, padx=10)
        
        self.datos_button = tk.Button(self.buttonsIndicatorsFrame, text="Datos", command=self.datos, state=tk.DISABLED)
        self.datos_button.grid(row=2, column=0, sticky='w', pady=5)
        
        self.datos_indicator = tk.Canvas(self.buttonsIndicatorsFrame, width=20, height=20)
        self.datos_indicator.create_oval(2, 2, 18, 18, fill="red")
        self.datos_indicator.grid(row=2, column=1, padx=10)
        
        # Right frame for the plot
        self.rightFrame = tk.Frame(root, bg="black")
        self.rightFrame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Upper frame for the 2D plot (set a weight for proportional resizing)
        self.upperFrame = tk.Frame(self.rightFrame, bg="black")
        self.upperFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)

        # Lower frame for the 3D plot (no weight needed, fills remaining space)
        self.lowerFrame = tk.Frame(self.rightFrame, bg="black")
        self.lowerFrame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        
        # Create a figure for Matplotlib for 2D plot
        self.fig1, self.ax1 = plt.subplots()
        self.fig1.patch.set_facecolor('black')
        self.ax1.axis('off')
        
        # Canvas for Matplotlib in Tkinter for 2D plot
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.upperFrame)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Interactor for vtk viewer. 
        # Crear el interactor de VTK
        self.vtk_widget = vtkTkRenderWindowInteractor(self.lowerFrame)
        self.vtk_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configurar el renderizador y la ventana de renderizado de VTK
        self.renderer = vtk.vtkRenderer()
        self.render_window = self.vtk_widget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        
        
         # Adding sliders for cut coordinates
        self.sliderFrame = tk.Frame(self.leftFrame)
        self.sliderFrame.pack(anchor='w')

        # Create row frames for each slider set (X, Y, Z)
        self.xRowFrame = tk.Frame(self.leftFrame)
        self.yRowFrame = tk.Frame(self.leftFrame)
        self.zRowFrame = tk.Frame(self.leftFrame)
        self.xRowFrame.pack(side=tk.TOP, anchor='w')
        self.yRowFrame.pack(side=tk.TOP, anchor='w')
        self.zRowFrame.pack(side=tk.TOP, anchor='w')

        # Create label and entry for X slider (in xRowFrame)
        self.xLabel = tk.Label(self.xRowFrame, text="X Coord:")
        self.xLabel.pack(side=tk.LEFT)

        self.xValue = tk.StringVar()
        self.xEntry = tk.Entry(self.xRowFrame, textvariable=self.xValue, width=5)
        self.xEntry.pack(side=tk.LEFT)
        self.xEntry.bind('<KeyRelease>', lambda event: self.update_slider("xSlider", self.xValue))

        self.xSlider = tk.Scale(self.xRowFrame, from_=-150, to=150, orient=tk.HORIZONTAL, showvalue=False)
        self.xSlider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.xSlider.bind("<ButtonRelease-1>", lambda event: self.update_value("xSlider", self.xValue))

        # Create label and entry for Y slider (in yRowFrame)
        self.yLabel = tk.Label(self.yRowFrame, text="Y Coord:")
        self.yLabel.pack(side=tk.LEFT)

        self.yValue = tk.StringVar()
        self.yEntry = tk.Entry(self.yRowFrame, textvariable=self.yValue, width=5)
        self.yEntry.pack(side=tk.LEFT)
        self.yEntry.bind('<KeyRelease>', lambda event: self.update_slider("ySlider", self.yValue))

        self.ySlider = tk.Scale(self.yRowFrame, from_=-150, to=150, orient=tk.HORIZONTAL, showvalue=False)
        self.ySlider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ySlider.bind("<ButtonRelease-1>", lambda event: self.update_value("ySlider", self.yValue))

        # Create label and entry for Z slider (in zRowFrame)
        self.zLabel = tk.Label(self.zRowFrame, text="Z Coord:")
        self.zLabel.pack(side=tk.LEFT)

        self.zValue = tk.StringVar()
        self.zEntry = tk.Entry(self.zRowFrame, textvariable=self.zValue, width=5)
        self.zEntry.pack(side=tk.LEFT)
        self.zEntry.bind('<KeyRelease>', lambda event: self.update_slider("zSlider", self.zValue))

        self.zSlider = tk.Scale(self.zRowFrame, from_=-150, to=150, orient=tk.HORIZONTAL, showvalue=False)
        self.zSlider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.zSlider.bind("<ButtonRelease-1>", lambda event: self.update_value("zSlider", self.zValue))
        
        # Initialize indicators
        self.update_value("xSlider", self.xValue)
        self.update_value("ySlider", self.yValue)
        self.update_value("zSlider", self.zValue)
        
        # Execution protocol for closure
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


    # Function to update X value in entry and potentially call showCuts (if needed)
    def update_value(self, slider_name, slider_variable, event=None):
        slider_variable.set(str(getattr(self, slider_name).get()))  # Get slider value
        if self.visualizeIndicator.itemcget(1,"fill") == "green":
                    self.showCuts()
        

    def update_slider(self, slider_name, entry_variable):
        try:
            value = int(entry_variable.get())
            if -150 <= value <= 150:
                getattr(self, slider_name).set(value)
                if self.visualizeIndicator.itemcget(1,"fill") == "green":
                    self.showCuts()
        except ValueError:
            pass


    def selectFolder(self):
        """
        Creates a filedialog to ask for the direcroty in which we want to work.
        When selected, it verifies its contents and determines wihch buttons it can enable.
            If there is no present segmentation, the visualization button stays disabled.
            Else, it loads the images
        """
        folderPath = filedialog.askdirectory()
        if folderPath:
            # Saves the path of the folder and displays it in the aplication.
            folderName = os.path.basename(folderPath)
            self.folderVar.set(folderName)
            self.folderLabel.config(text=f"Carpeta seleccionada: {folderName}")
            
            # Search for the brain and segmentation volumes on the directories.
            self.loadImages(folderPath)
            
            # Verifies if the volumes are found
            if self.img is not None: 
                # Determine which segments are present.
                self.segmentsDF = presentSegments(self.img)
                self.segments = self.segmentsDF['StructName'].tolist() # Create a list with the segments.
                self.segments[0] = "All"
                #Create a color map and dictionary of the segmentations
                self.cmap, self.colors = lColorMap()
                
                # Enable visualization button
                self.visualizeButton.config(state=tk.NORMAL)
                # Create a combobox to show the present segmentations.
                self.segmentations_var = tk.StringVar()
                self.segmentations_combobox = ttk.Combobox(self.leftFrame, 
                    textvariable=self.segmentations_var,
                    values=self.segments,
                    state="readonly")
                self.segmentations_combobox.pack(anchor='w', pady=5)
                self.segmentations_combobox.bind("<<ComboboxSelected>>", self.segment_selected)
            # Habilitar el resto de botones.
            self.segmentar_button.config(state=tk.NORMAL)
            self.datos_button.config(state=tk.NORMAL)
    
    def toggleIndicator(self, indicator):
        """
        Toggles the color and therefore state of an indicator.
        
        """
        currentColor = indicator.itemcget(1, "fill")
        newColor = "green" if currentColor == "red" else "red"
        indicator.itemconfig(1, fill=newColor)
    
    def visualize(self):
        """
        Displays the roi and 3d mesh of the current Segmentation.
        
        """
        # Alternate the toggle state.
        self.toggleIndicator(self.visualizeIndicator)
        if self.visualizeIndicator.itemcget(1,"fill") == "green":
            self.showCuts()
            self.viewVolume()
            print("visualize On")
        else: 
            self.clearPlots()
            print("visualize Off")
    
    def segmentar(self):
        """
        To be implemented. Calls the script segment the present volumes.
        """
        # Alternate the toggle state.
        self.toggleIndicator(self.segmentar_indicator)
        print("Segmentar")
    
    def datos(self):
        """
        To be implemented shortly. Reads the created file with the corresponding information of the actual volume. 
        If no file is encountered. It calls for the script to find such information.
        """
        # Alternate the toggle state.
        self.toggleIndicator(self.datos_indicator)
        print("Datos")
    
        
    def loadImages(self, folderPath):
        """
        finds and loadsthe
        """
        for root, dirs, files in os.walk(folderPath):
            if "aparc+aseg.mgz" in files:
                imgPath = os.path.join(root, "aparc+aseg.mgz")
                self.img = nib.load(imgPath)
                self.imgData = self.img.get_fdata()
                print(f"Found Segmentation Volume: {imgPath}")
            if "brain.mgz" in files:
                brainPath = os.path.join(root, "brain.mgz")
                self.brain = nib.load(brainPath)
                self.brain_data = self.brain.get_fdata()
                print(f"Found Brain Volume: {brainPath}")
        if self.img is None:
            print("Segmentations volume not found")
        if self.brain is None:
            print("Brain volume not found")
        
    
    def segment_selected(self, event):
        # Get the segment that was selected.
        selected_segment = self.segmentations_var.get()
        print(f"Segmentación seleccionada: {selected_segment}")
        if selected_segment == "All":
            self.segment = self.img
            self.color = self.cmap
        else:
            self.getSegment(selected_segment)
            
        # Determines if the Visualization button is acctive. Or if the plots must be cleared.
        if self.visualizeIndicator.itemcget(1,"fill") == "green":
            self.showCuts()
            self.viewVolume()
        else:
            self.clearPlots()
        
    def getSegment(self, segment):
        for _, row in self.segmentsDF.iterrows():
        # Check if it's not the first row and the NVoxels value is greater than 1
            colorId, name= row[['Id', 'StructName']]
            if name == segment:                
                self.color = ListedColormap([self.colors[colorId]])
                # Create a boolean mask for imgData values that match the ColorId value
                mask = (self.imgData == colorId)
                
                # Apply the logical mask
                maskData = np.where(mask, colorId, 0)
                self.segment = image.new_img_like(self.img, maskData.astype(np.int32))
            
    
    def showCuts(self, event=None):
        if self.visualizeIndicator.itemcget(1, "fill") == "green":
            self.fig1.clear()
            self.ax1 = self.fig1.add_subplot(111)
            self.ax1.axis('off')
            
            # Get the current cut coordinates from sliders
            x = self.xSlider.get()
            y = self.ySlider.get()
            z = self.zSlider.get()

            # Plotting the ROI
            plotting.plot_roi(self.segment, black_bg=True, bg_img=self.brain, 
                                    cut_coords=(x,y,z), cmap=self.color, display_mode='ortho', axes=self.ax1)
            
            # Redraw the canvas.
            self.canvas1.draw()
      
    
    def viewVolume(self):
        """
        Función para visualizar un volumen MRI utilizando VTK y asignando colores por etiqueta única.

        Parámetros:
            imgData: Arreglo NumPy que contiene los datos del volumen MRI.

        Retorna:
            None: La función no retorna nada, solo muestra la visualización.
        """
        # Get data from the volume
        imgData = self.img.get_fdata()
        segData = self.segment.get_fdata()
        
        # Convert the numpy array to a VTK image data object
        self.vtk_data = vtk.vtkImageData()
        self.vtk_data.SetDimensions(imgData.shape)
        self.vtk_data.SetSpacing(self.img.header.get_zooms())

        
        self.flat_data = imgData.ravel(order='F')  # Flatten the numpy array
        self.vtk_flat_data = numpy_to_vtk(num_array=self.flat_data, deep=True, array_type=vtk.VTK_FLOAT)
        self.vtk_data.GetPointData().SetScalars(self.vtk_flat_data)


        # Create transfer mapping scalar value to opacity
        self.opacityTransferFunction = vtk.vtkPiecewiseFunction()
        self.opacityTransferFunction.AddPoint(0, 0.0)

        # Create transfer mapping scalar value to color
        self.colorTransferFunction = vtk.vtkColorTransferFunction()
        
        # Get the unique labels of the segmentation volume and designate their color.
        segIds = np.unique(segData)
        for i in np.unique(imgData):
            if i>0:
                if i in segIds:
                    rgb = self.colors[i]
                    self.colorTransferFunction.AddRGBPoint(i, rgb[0], rgb[1], rgb[2])
                    self.opacityTransferFunction.AddPoint(i, 0.9)
                else:
                    self.opacityTransferFunction.AddPoint(i, 0.01)  # Very translucent
                    self.colorTransferFunction.AddRGBPoint(i, 0.5, 0.5, 0.5)  # Black
            
        # Create a volume rendering
        self.volumeProperty = vtk.vtkVolumeProperty()
        self.volumeProperty.SetColor(self.colorTransferFunction)
        self.volumeProperty.SetScalarOpacity(self.opacityTransferFunction)
        #self.volumeProperty.SetInterpolationTypeToLinear()
            
            # The mapper / ray cast function know how to render the data
        self.volumeMapper = vtk.vtkFixedPointVolumeRayCastMapper()
        self.volumeMapper.SetInputData(self.vtk_data)
            
        # The volume holds the mapper and the property and can be used to position/orient the volume
        self.volume = vtk.vtkVolume()
        self.volume.SetMapper(self.volumeMapper)
        self.volume.SetProperty(self.volumeProperty)
            
        # Crear el renderizador, la ventana de renderizado y el interactor
         # Clear previous volumes
        self.renderer.RemoveAllViewProps()
        
        # Añadir el volumen al renderizador
        self.renderer.AddVolume(self.volume)
        self.renderer.SetBackground(0,0,0)  # Fondo negro
        
        # Center the volume in the renderer
        self.renderer.ResetCamera()

        # Iniciar el interactor de VTK
    
        self.vtk_widget.Initialize()
        self.vtk_widget.Render()
        self.vtk_widget.Start()


    def clearPlots(self):
        # Clear the existing plots
        self.fig1.clear()
        self.ax1 = self.fig1.add_subplot(111)
        self.ax1.axis('off')

    def on_closing(self):
        # Destroy vtkRenderWindow before closing.
        self.vtk_widget.Finalize()
        self.vtk_widget.TerminateApp()
        self.root.destroy()
        

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
