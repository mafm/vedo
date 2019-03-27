from __future__ import division, print_function
import time
import sys
import vtk
import numpy

from vtkplotter import __version__
import vtkplotter.vtkio as vtkio
import vtkplotter.utils as utils
import vtkplotter.colors as colors
from vtkplotter.actors import Actor, Volume
import vtkplotter.docs as docs
import vtkplotter.settings as settings
import vtkplotter.addons as addons

__doc__ = (
    """
Defines main class ``Plotter`` to manage actors and 3D rendering.
"""
    + docs._defs
)

__all__ = ["show", "clear", "Plotter"]


########################################################################
def show(*actors, **options
#    at=None,
#    shape=(1, 1),
#    N=None,
#    pos=(0, 0),
#    size="auto",
#    screensize="auto",
#    title="",
#    bg="blackboard",
#    bg2=None,
#    axes=4,
#    infinity=False,
#    verbose=True,
#    interactive=None,
#    offscreen=False,
#    resetcam=True,
#    zoom=None,
#    viewup="",
#    azimuth=0,
#    elevation=0,
#    roll=0,
#    interactorStyle=0,
#    newPlotter=False,
#    depthpeeling=False,
#    q=False,
):
    """
    Create on the fly an instance of class ``Plotter`` and show the object(s) provided.

    Allowed input objects are: ``filename``, ``vtkPolyData``, ``vtkActor``, 
    ``vtkActor2D``, ``vtkImageActor``, ``vtkAssembly`` or ``vtkVolume``.

    If filename is given, its type is guessed based on its extension.
    Supported formats are: 
    `vtu, vts, vtp, ply, obj, stl, 3ds, xml, neutral, gmsh, pcd, xyz, txt, byu,
    tif, slc, vti, mhd, png, jpg`.

    :param bool newPlotter: if set to `True`, a call to ``show`` will instantiate
        a new ``Plotter`` object (a new window) instead of reusing the first created.
        See e.g.: |readVolumeAsIsoSurface.py|_
    :return: the current ``Plotter`` class instance.

    .. note:: With multiple renderers, keyword ``at`` can become a `list`, e.g.

        .. code-block:: python
        
            from vtkplotter import *
            s = Sphere()
            c = Cube()
            p = Paraboloid()
            show(s, c, at=[0, 1], shape=(3,1))
            show(p, at=2, interactive=True)
            #
            # is equivalent to:
            vp = Plotter(shape=(3,1))
            s = Sphere()
            c = Cube()
            p = Paraboloid()
            vp.show(s, at=0)
            vp.show(p, at=1)
            vp.show(c, at=2, interactive=True)
    """
    at = options.pop("at", None)
    shape = options.pop("shape", (1, 1))
    N = options.pop("N", None)
    pos = options.pop("pos", (0, 0))
    size = options.pop("size", "auto")
    screensize = options.pop("screensize", "auto")
    title = options.pop("title", "")
    bg = options.pop("bg", "blackboard")
    bg2 = options.pop("bg2", None)
    axes = options.pop("axes", 4)
    infinity = options.pop("infinity", False)
    verbose = options.pop("verbose", True)
    interactive = options.pop("interactive", None)
    offscreen = options.pop("offscreen", False)
    resetcam = options.pop("resetcam", True)
    zoom = options.pop("zoom", None)
    viewup = options.pop("viewup", "")
    azimuth = options.pop("azimuth", 0)
    elevation = options.pop("elevation", 0)
    roll = options.pop("roll", 0)
    interactorStyle = options.pop("interactorStyle", 0)
    newPlotter = options.pop("newPlotter", False)
    depthpeeling = options.pop("depthpeeling", False)
    q = options.pop("q", False)

    if len(actors) == 0:
        actors = None
    elif len(actors) == 1:
        actors = actors[0]
    else:
        actors = utils.flatten(actors)            
    
    if settings.plotter_instance and newPlotter == False:
        vp = settings.plotter_instance
    else:
        if utils.isSequence(at):
            if not utils.isSequence(actors):
                colors.printc("~times show() Error: input must be a list.", c=1)
                exit()
            if len(at) != len(actors):
                colors.printc("~times show() Error: lists 'input' and 'at', must have equal lengths.", c=1)
                exit()
            if len(at) > 1 and (shape == (1, 1) and N == None):
                N = max(at) + 1
        elif at is None and (N or shape != (1, 1)):
            if not utils.isSequence(actors):
                colors.printc('~times show() Error: N or shape is set, but input is not a sequence.', c=1)
                colors.printc('              you may need to specify e.g. at=0', c=1)
                exit()
            at = range(len(actors))
        
#        if settings.plotter_instance:
#            prevcam = settings.plotter_instance.camera
#            prevsharecam = settings.plotter_instance.sharecam
#        else:
#            prevcam = False

        vp = Plotter(
            shape=shape,
            N=N,
            pos=pos,
            size=size,
            screensize=screensize,
            title=title,
            bg=bg,
            bg2=bg2,
            axes=axes,
            infinity=infinity,
            depthpeeling=depthpeeling,
            verbose=verbose,
            interactive=interactive,
            offscreen=offscreen,
        )
        
#        if prevcam:
#            vp.camera = prevcam
            

    if utils.isSequence(at):
        for i, a in enumerate(actors):
            vp.show(
                a,
                at=i,
                zoom=zoom,
                resetcam=resetcam,
                viewup=viewup,
                azimuth=azimuth,
                elevation=elevation,
                roll=roll,
                interactive=interactive,
                interactorStyle=interactorStyle,
                q=q,
            )
        vp.interactor.Start()
    else:
        vp.show(
            actors,
            at=at,
            zoom=zoom,
            viewup=viewup,
            azimuth=azimuth,
            elevation=elevation,
            roll=roll,
            interactive=interactive,
            interactorStyle=interactorStyle,
            q=q,
        )

    return vp


def clear(actor=()):
    """
    Clear specific actor or list of actors from the current rendering window.
    """
    if not settings.plotter_instance:
        return
    settings.plotter_instance.clear(actor)
    return settings.plotter_instance


def plotMatrix(M, title='matrix', continuous=True, cmap='Greys'):
    """
	 Plot a matrix using `matplotlib`.
    
    :Example:
        .. code-block:: python

            from vtkplotter.dolfin import plotMatrix
            import numpy as np
            
            M = np.eye(9) + np.random.randn(9,9)/4
            
            plotMatrix(M)
        
        |pmatrix|
    """
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    
    M    = numpy.array(M)
    m,n  = numpy.shape(M)
    M    = M.round(decimals=2)

    fig  = plt.figure()
    ax   = fig.add_subplot(111)
    cmap = mpl.cm.get_cmap(cmap)
    if not continuous:
        unq  = numpy.unique(M)
    im      = ax.imshow(M, cmap=cmap, interpolation='None')
    divider = make_axes_locatable(ax)
    cax     = divider.append_axes("right", size="5%", pad=0.05)
    dim     = r'$%i \times %i$ ' % (m,n)
    ax.set_title(dim + title)
    ax.axis('off')
    cb = plt.colorbar(im, cax=cax)
    if not continuous:
       cb.set_ticks(unq)
       cb.set_ticklabels(unq)
    plt.show()
    
    
########################################################################
class Plotter:
    """
    Main class to manage actors.

    :param list shape: shape of the grid of renderers in format (rows, columns). 
        Ignored if N is specified.
    :param int N: number of desired renderers arranged in a grid automatically.
    :param list pos: (x,y) position in pixels of top-left corneer of the rendering window 
        on the screen
    :param size: size of the rendering window. If 'auto', guess it based on screensize.
    :param screensize: physical size of the monitor screen 
    :param bg: background color or specify jpg image file name with path
    :param bg2: background color of a gradient towards the top
    :param int axes:  

      - 0,  no axes,
      - 1,  draw three gray grid walls
      - 2,  show cartesian axes from (0,0,0)
      - 3,  show positive range of cartesian axes from (0,0,0)
      - 4,  show a triad at bottom left
      - 5,  show a cube at bottom left
      - 6,  mark the corners of the bounding box
      - 7,  draw a simple ruler at the bottom of the window
      - 8,  show the ``vtkCubeAxesActor`` object,
      - 9,  show the bounding box outLine,

    :param bool infinity: if True fugue point is set at infinity (no perspective effects)
    :param bool sharecam: if False each renderer will have an independent vtkCamera
    :param bool interactive: if True will stop after show() to allow interaction w/ window
    :param bool offscreen: if True will not show the rendering window    
    :param bool depthpeeling: depth-peel volumes along with the translucent geometry

    |multiwindows|
    """

    def __init__(
        self,
        shape=(1, 1),
        N=None,
        pos=(0, 0),
        size="auto",
        screensize="auto",
        title="",
        bg="blackboard",
        bg2=None,
        axes=4,
        infinity=False,
        sharecam=True,
        verbose=True,
        interactive=None,
        offscreen=False,
        depthpeeling=False,
    ):

        settings.plotter_instance = self
        settings.plotter_instances.append(self)

        if interactive is None:
            if N or shape != (1, 1):
                interactive = False
            else:
                interactive = True

        if not interactive:
            verbose = False

        self.verbose = verbose
        self.actors = []  # list of actors to be shown
        self.clickedActor = None  # holds the actor that has been clicked
        self.renderer = None  # current renderer
        self.renderers = []  # list of renderers
        self.shape = shape
        self.pos = pos
        self.size = [size[1], size[0]]  # size of the rendering window
        self.interactive = interactive  # allows to interact with renderer
        self.axes = axes  # show axes type nr.
        self.title = title  # window title
        self.xtitle = "x"  # x axis label and units
        self.ytitle = "y"  # y axis label and units
        self.ztitle = "z"  # z axis label and units
        self.sharecam = sharecam  # share the same camera if multiple renderers
        self.infinity = infinity  # ParallelProjection On or Off
        self._legend = []  # list of legend entries for actors
        self.legendSize = 0.15  # size of legend
        self.legendBC = (0.96, 0.96, 0.9)  # legend background color
        self.legendPos = 2  # 1=topright, 2=top-right, 3=bottom-left
        self.picked3d = None  # 3d coords of a clicked point on an actor
        self.backgrcol = bg
        self.offscreen = offscreen
        self.showFrame = True

        # mostly internal stuff:
        self.camThickness = None
        self.justremoved = None
        self.axes_exist = []
        self.icol = 0
        self.clock = 0
        self._clockt0 = time.time()
        self.initializedPlotter = False
        self.initializedIren = False
        self.camera = vtk.vtkCamera()
        self.keyPressFunction = None
        self.sliders = []
        self.buttons = []
        self.widgets = []
        self.scalarbars = []
        self.cutterWidget = None
        self.backgroundRenderer = None
        self.mouseLeftClickFunction = None
        self.mouseMiddleClickFunction = None
        self.mouseRightClickFunction = None

        # sort out screen size
        self.window = vtk.vtkRenderWindow()
        self.window.PointSmoothingOn()
        if screensize == "auto":
            aus = self.window.GetScreenSize()
            if aus and len(aus) == 2 and aus[0] > 100 and aus[1] > 100:  # seems ok
                if aus[0] / aus[1] > 2:  # looks like there are 2 or more screens
                    screensize = (int(aus[0] / 2), aus[1])
                else:
                    screensize = aus
            else:  # it went wrong, use a default 1.5 ratio
                screensize = (2160, 1440)

        x, y = screensize
        if N:  # N = number of renderers. Find out the best
            if shape != (1, 1):  # arrangement based on minimum nr. of empty renderers
                colors.printc("Warning: having set N, shape is ignored.", c=1)
            nx = int(numpy.sqrt(int(N * y / x) + 1))
            ny = int(numpy.sqrt(int(N * x / y) + 1))
            lm = [
                (nx, ny),
                (nx, ny + 1),
                (nx - 1, ny),
                (nx + 1, ny),
                (nx, ny - 1),
                (nx - 1, ny + 1),
                (nx + 1, ny - 1),
                (nx + 1, ny + 1),
                (nx - 1, ny - 1),
            ]
            ind, minl = 0, 1000
            for i, m in enumerate(lm):
                l = m[0] * m[1]
                if N <= l < minl:
                    ind = i
                    minl = l
            shape = lm[ind]
        if size == "auto":  # figure out a reasonable window size
            f = 1.5
            xs = y / f * shape[1]  # because y<x
            ys = y / f * shape[0]
            if xs > x / f:  # shrink
                xs = x / f
                ys = xs / shape[1] * shape[0]
            if ys > y / f:
                ys = y / f
                xs = ys / shape[0] * shape[1]
            self.size = (int(xs), int(ys))
            if shape == (1, 1):
                self.size = (int(y / f), int(y / f))  # because y<x

        ############################
        # build the renderers scene:
        self.shape = shape

        if sum(shape) > 3:
            self.legendSize *= 2

        for i in reversed(range(shape[0])):
            for j in range(shape[1]):
                arenderer = vtk.vtkRenderer()
                arenderer.SetUseDepthPeeling(depthpeeling)
                if "jpg" in str(bg).lower() or "jpeg" in str(bg).lower():
                    if i == 0:
                        jpeg_reader = vtk.vtkJPEGReader()
                        if not jpeg_reader.CanReadFile(bg):
                            colors.printc("~times Error reading background image file", bg, c=1)
                            sys.exit()
                        jpeg_reader.SetFileName(bg)
                        jpeg_reader.Update()
                        image_data = jpeg_reader.GetOutput()
                        image_actor = vtk.vtkImageActor()
                        image_actor.InterpolateOn()
                        image_actor.SetInputData(image_data)
                        self.backgroundRenderer = vtk.vtkRenderer()
                        self.backgroundRenderer.SetLayer(0)
                        self.backgroundRenderer.InteractiveOff()
                        if bg2:
                            self.backgroundRenderer.SetBackground(colors.getColor(bg2))
                        else:
                            self.backgroundRenderer.SetBackground(1, 1, 1)
                        arenderer.SetLayer(1)
                        self.window.SetNumberOfLayers(2)
                        self.window.AddRenderer(self.backgroundRenderer)
                        self.backgroundRenderer.AddActor(image_actor)
                else:
                    arenderer.SetBackground(colors.getColor(bg))
                    if bg2:
                        arenderer.GradientBackgroundOn()
                        arenderer.SetBackground2(colors.getColor(bg2))
                x0 = i / shape[0]
                y0 = j / shape[1]
                x1 = (i + 1) / shape[0]
                y1 = (j + 1) / shape[1]
                arenderer.SetViewport(y0, x0, y1, x1)
                self.renderers.append(arenderer)
                self.axes_exist.append(None)

        if "full" in size and not offscreen:  # full screen
            self.window.SetFullScreen(True)
            self.window.BordersOn()
        else:
            self.window.SetSize(int(self.size[0]), int(self.size[1]))

        self.window.SetPosition(pos)

        if not title:
            title = " vtkplotter " + __version__ + ", vtk " + vtk.vtkVersion().GetVTKVersion()
            title += ", python " + str(sys.version_info[0]) + "." + str(sys.version_info[1])

        self.window.SetWindowName(title)

        if not settings.usingQt:
            for r in self.renderers:
                self.window.AddRenderer(r)

        if offscreen:
            self.window.SetOffScreenRendering(True)
            self.interactive = False
            self.interactor = None
            ######
            return
            ######

        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetRenderWindow(self.window)
        vsty = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(vsty)

        self.interactor.AddObserver("LeftButtonPressEvent", vtkio._mouseleft)
        self.interactor.AddObserver("RightButtonPressEvent", vtkio._mouseright)
        self.interactor.AddObserver("MiddleButtonPressEvent", vtkio._mousemiddle)
        self.interactor.AddObserver("KeyPressEvent", vtkio._keypress)
        #self.interactor.AddObserver("EnterEvent", vtkio._mouse_enter)

        if settings.allowInteraction:
            self._update_observer = None
            self._update_win_clock = time.time()

            def win_interact(iren, event):  # flushing renderer events
                if event == "TimerEvent":
                    iren.TerminateApp()

            self.interactor.AddObserver("TimerEvent", win_interact)

            def _allowInteraction():
                timenow = time.time()
                if timenow - self._update_win_clock > 0.1:
                    self._update_win_clock = timenow
                    self._update_observer = self.interactor.CreateRepeatingTimer(1)
                    self.interactor.Start()
                    self.interactor.DestroyTimer(self._update_observer)

            self.allowInteraction = _allowInteraction

    ####################################################
    def load(
        self,
        inputobj,
        c="gold",
        alpha=1,
        wire=False,
        bc=None,
        texture=None,
        smoothing=None,
        threshold=None,
        connectivity=False,
    ):
        """ 
        Returns a ``vtkActor`` from reading a file, directory or ``vtkPolyData``.

        :param c: color in RGB format, hex, symbol or name
        :param alpha:   transparency (0=invisible)
        :param wire:    show surface as wireframe
        :param bc:      backface color of internal surface
        :param texture: any png/jpg file can be used as texture

        For volumetric data (tiff, slc, vti files):

        :param smoothing:    gaussian filter to smooth vtkImageData
        :param threshold:    value to draw the isosurface
        :param bool connectivity: if True only keeps the largest portion of the polydata
        """
        acts = vtkio.load(inputobj, c, alpha, wire, bc, texture, smoothing, threshold, connectivity)
        if utils.isSequence(acts):
            self.actors += acts
        else:
            self.actors.append(acts)
        return acts


    def getActors(self, obj=None, renderer=None):
        """
        Return an actors list.

        If ``obj`` is:
            ``None``, return actors of current renderer

            ``int``, return actors in given renderer number 

            ``vtkAssembly`` return the contained actors

            ``string``, return actors matching legend name

        :param int,vtkRenderer renderer: specify which renederer to look into.
        """
        if renderer is None:
            renderer = self.renderer
        elif isinstance(renderer, int):
                renderer = self.renderers.index(renderer)

        if not renderer:
            return []

        if obj is None or isinstance(obj, int):
            if obj is None:
                acs = renderer.GetActors()
            elif obj >= len(self.renderers):
                colors.printc("~timesError in getActors: non existing renderer", obj, c=1)
                return []
            else:
                acs = self.renderers[obj].GetActors()
            actors = []
            acs.InitTraversal()
            for i in range(acs.GetNumberOfItems()):
                a = acs.GetNextItem()
                if a.GetPickable():
                    r = self.renderers.index(renderer)
                    if a == self.axes_exist[r]:
                        continue
                    actors.append(a)
            return actors

        elif isinstance(obj, vtk.vtkAssembly):
            cl = vtk.vtkPropCollection()
            obj.GetActors(cl)
            actors = []
            cl.InitTraversal()
            for i in range(obj.GetNumberOfPaths()):
                act = vtk.vtkActor.SafeDownCast(cl.GetNextProp())
                if act.GetPickable():
                    actors.append(act)
            return actors

        elif isinstance(obj, str):  # search the actor by the legend name
            actors = []
            for a in self.actors:
                if hasattr(a, "_legend") and obj in a._legend and a.GetPickable():
                    actors.append(a)
            return actors

        elif isinstance(obj, vtk.vtkActor):
            return [obj]

        if self.verbose:
            colors.printc("~lightning Warning in getActors: unexpected input type", obj, c=1)
        return []

    def add(self, actors):
        """Append input object to the internal list of actors to be shown.

        :return: returns input actor for possible concatenation.
        """
        if utils.isSequence(actors):
            for a in actors:
                if a not in self.actors:
                    self.actors.append(a)
            return None
        else:
            self.actors.append(actors)
            return actors

    def moveCamera(self, camstart, camstop, fraction):
        """
        Takes as input two ``vtkCamera`` objects and returns a
        new ``vtkCamera`` that is at an intermediate position:

        fraction=0 -> camstart,  fraction=1 -> camstop.

        Press ``shift-C`` key in interactive mode to dump a python snipplet
        of parameters for the current camera view.
        """
        if isinstance(fraction, int):
            colors.printc("~lightning Warning in moveCamera(): fraction should not be an integer", c=1)
        if fraction > 1:
            colors.printc("~lightning Warning in moveCamera(): fraction is > 1", c=1)
        cam = vtk.vtkCamera()
        cam.DeepCopy(camstart)
        p1 = numpy.array(camstart.GetPosition())
        f1 = numpy.array(camstart.GetFocalPoint())
        v1 = numpy.array(camstart.GetViewUp())
        c1 = numpy.array(camstart.GetClippingRange())
        s1 = camstart.GetDistance()

        p2 = numpy.array(camstop.GetPosition())
        f2 = numpy.array(camstop.GetFocalPoint())
        v2 = numpy.array(camstop.GetViewUp())
        c2 = numpy.array(camstop.GetClippingRange())
        s2 = camstop.GetDistance()
        cam.SetPosition(p2 * fraction + p1 * (1 - fraction))
        cam.SetFocalPoint(f2 * fraction + f1 * (1 - fraction))
        cam.SetViewUp(v2 * fraction + v1 * (1 - fraction))
        cam.SetDistance(s2 * fraction + s1 * (1 - fraction))
        cam.SetClippingRange(c2 * fraction + c1 * (1 - fraction))
        self.camera = cam
        save_int = self.interactive
        self.show(resetcam=0, interactive=0)
        self.interactive = save_int

    def light(
        self,
        pos=(1, 1, 1),
        fp=(0, 0, 0),
        deg=25,
        diffuse="y",
        ambient="r",
        specular="b",
        showsource=False,
    ):
        """
        Generate a source of light placed at pos, directed to focal point fp.

        :param fp: focal Point, if this is a ``vtkActor`` use its position.
        :type fp: vtkActor, list
        :param deg: aperture angle of the light source
        :param showsource: if `True`, will show a vtk representation
                            of the source of light as an extra actor

        .. hint:: |lights.py|_
        """
        if isinstance(fp, vtk.vtkActor):
            fp = fp.GetPosition()
        light = vtk.vtkLight()
        light.SetLightTypeToSceneLight()
        light.SetPosition(pos)
        light.SetPositional(1)
        light.SetConeAngle(deg)
        light.SetFocalPoint(fp)
        light.SetDiffuseColor(colors.getColor(diffuse))
        light.SetAmbientColor(colors.getColor(ambient))
        light.SetSpecularColor(colors.getColor(specular))
        save_int = self.interactive
        self.show(interactive=0)
        self.interactive = save_int
        if showsource:
            lightActor = vtk.vtkLightActor()
            lightActor.SetLight(light)
            self.renderer.AddViewProp(lightActor)
            self.renderer.AddLight(light)
        return light

    ################################################################## AddOns
    def addScalarBar(self, actor=None, c=None, title="", horizontal=False, vmin=None, vmax=None):
        """Add a 2D scalar bar for the specified actor.

        If `actor` is ``None`` will add it to the last actor in ``self.actors``.

        .. hint:: |mesh_bands| |mesh_bands.py|_
        """
        return addons.addScalarBar(actor, c, title, horizontal, vmin, vmax)

    def addScalarBar3D(
        self,
        obj=None,
        at=0,
        pos=(0, 0, 0),
        normal=(0, 0, 1),
        sx=0.1,
        sy=2,
        nlabels=9,
        ncols=256,
        cmap=None,
        c="k",
        alpha=1,
    ):
        """Draw a 3D scalar bar.

        ``obj`` input can be:
            - a list of numbers,
            - a list of two numbers in the form `(min, max)`,
            - a ``vtkActor`` already containing a set of scalars associated to vertices or cells,
            - if ``None`` the last actor in the list of actors will be used.

        .. hint:: |mesh_coloring| |mesh_coloring.py|_
        """
        return addons.addScalarBar3D(obj, at, pos, normal, sx, sy, nlabels, ncols, cmap, c, alpha)

    def addSlider2D(
        self, sliderfunc, xmin, xmax, value=None, pos=4, s=0.04, title="", c=None, showValue=True
    ):
        """Add a slider widget which can call an external custom function.

        :param sliderfunc: external function to be called by the widget
        :param float xmin:  lower value
        :param float xmax:  upper value
        :param float value: current value
        :param list pos:  position corner number: horizontal [1-4] or vertical [11-14]
                            it can also be specified by corners coordinates [(x1,y1), (x2,y2)]
        :param str title: title text
        :param bool showValue:  if true current value is shown

        .. hint:: |sliders| |sliders.py|_
        """
        return addons.addSlider2D(sliderfunc, xmin, xmax, value, pos, s, title, c, showValue)

    def addSlider3D(
        self,
        sliderfunc,
        pos1,
        pos2,
        xmin,
        xmax,
        value=None,
        s=0.03,
        title="",
        rotation=0,
        c=None,
        showValue=True,
    ):
        """Add a 3D slider widget which can call an external custom function.

        :param sliderfunc: external function to be called by the widget
        :param list pos1: first position coordinates
        :param list pos2: second position coordinates
        :param float xmin:  lower value
        :param float xmax:  upper value
        :param float value: initial value
        :param float s: label scaling factor
        :param str title: title text
        :param c: slider color
        :param float rotation: title rotation around slider axis
        :param bool showValue: if True current value is shown

        .. hint:: |sliders3d| |sliders3d.py|_
        """
        return addons.addSlider3D(
            sliderfunc, pos1, pos2, xmin, xmax, value, s, title, rotation, c, showValue
        )

    def addButton(
        self,
        fnc,
        states=("On", "Off"),
        c=("w", "w"),
        bc=("dg", "dr"),
        pos=[20, 40],
        size=24,
        font="arial",
        bold=False,
        italic=False,
        alpha=1,
        angle=0,
    ):
        """Add a button to the renderer window.
        
        :param list states: a list of possible states ['On', 'Off']
        :param c:      a list of colors for each state
        :param bc:     a list of background colors for each state
        :param pos:    2D position in pixels from left-bottom corner
        :param size:   size of button font
        :param str font:   font type (arial, courier, times)
        :param bool bold:   bold face (False)
        :param bool italic: italic face (False)
        :param float alpha:  opacity level
        :param float angle:  anticlockwise rotation in degrees

        .. hint:: |buttons| |buttons.py|_
        """
        return addons.addButton(fnc, states, c, bc, pos, size, font, bold, italic, alpha, angle)

    def addCutterTool(self, actor):
        """Create handles to cut away parts of a mesh.

        .. hint:: |cutter| |cutter.py|_
        """
        return addons.addCutterTool(actor)

    def addIcon(self, iconActor, pos=3, size=0.08):
        """Add an inset icon mesh into the same renderer.

        :param pos: icon position in the range [1-4] indicating one of the 4 corners,
                    or it can be a tuple (x,y) as a fraction of the renderer size.
        :param float size: size of the square inset.

        .. hint:: |icon| |icon.py|_
        """
        return addons.addIcon(iconActor, pos, size)

    def addAxes(self, axtype=None, c=None):
        """Draw axes on scene. Available axes types:

        :param int axtype: 

              - 0,  no axes,
              - 1,  draw three gray grid walls
              - 2,  show cartesian axes from (0,0,0)
              - 3,  show positive range of cartesian axes from (0,0,0)
              - 4,  show a triad at bottom left
              - 5,  show a cube at bottom left
              - 6,  mark the corners of the bounding box
              - 7,  draw a simple ruler at the bottom of the window
              - 8,  show the ``vtkCubeAxesActor`` object
              - 9,  show the bounding box outLine
              - 10, show three circles representing the maximum bounding box
        """
        return addons.addAxes(axtype, c)

    def addLegend(self):
        return addons.addLegend()

    ##############################################################################
    def show(
        self,
        *actors, **options
#        at=None,
#        axes=None,
#        c=None,
#        alpha=None,
#        wire=False,
#        bc=None,
#        resetcam=True,
#        zoom=False,
#        interactive=None,
#        rate=None,
#        viewup="",
#        azimuth=0,
#        elevation=0,
#        roll=0,
#        interactorStyle=0,
#        q=False,
    ):
        """
        Render a list of actors.

        Allowed input objects are: ``filename``, ``vtkPolyData``, ``vtkActor``, 
        ``vtkActor2D``, ``vtkImageActor``, ``vtkAssembly`` or ``vtkVolume``.

        If filename is given, its type is guessed based on its extension.
        Supported formats are: 
        `vtu, vts, vtp, ply, obj, stl, 3ds, xml, neutral, gmsh, pcd, xyz, txt, byu,
        tif, slc, vti, mhd, png, jpg`.

        :param int at: number of the renderer to plot to, if more than one exists
        :param int axes: set the type of axes to be shown

              - 0,  no axes,
              - 1,  draw three gray grid walls
              - 2,  show cartesian axes from (0,0,0)
              - 3,  show positive range of cartesian axes from (0,0,0)
              - 4,  show a triad at bottom left
              - 5,  show a cube at bottom left
              - 6,  mark the corners of the bounding box
              - 7,  draw a simple ruler at the bottom of the window
              - 8,  show the ``vtkCubeAxesActor`` object,
              - 9,  show the bounding box outLine,
              - 10, show three circles representing the maximum bounding box

        :param c:     surface color, in rgb, hex or name formats
        :param bc:    set a color for the internal surface face
        :param bool wire:  show actor in wireframe representation
        :param float azimuth/elevation/roll:  move camera accordingly
        :param str viewup:  either ['x', 'y', 'z'] or a vector to set vertical direction
        :param bool resetcam:  re-adjust camera position to fit objects
        :param bool interactive:  pause and interact with window (True) 
            or continue execution (False)
        :param float rate:  maximum rate of `show()` in Hertz
        :param int interactorStyle: set the type of interaction

            - 0, TrackballCamera
            - 1, TrackballActor
            - 2, JoystickCamera
            - 3, Unicam
            - 4, Flight
            - 5, RubberBand3D
            - 6, RubberBandZoom

        :param bool q:  force program to quit after `show()` command returns.
        """
        at = options.pop("at", None)
        axes = options.pop("axes", None)
        c = options.pop("c", None)
        alpha = options.pop("alpha", None)
        wire = options.pop("wire", False)
        bc = options.pop("bc", None)
        resetcam = options.pop("resetcam", True)
        zoom = options.pop("zoom", False)
        interactive = options.pop("interactive", None)
        rate = options.pop("rate", None)
        viewup = options.pop("viewup", "")
        azimuth = options.pop("azimuth", 0)
        elevation = options.pop("elevation", 0)
        roll = options.pop("roll", 0)
        interactorStyle = options.pop("interactorStyle", 0)
        q = options.pop("q", False)

        if self.offscreen:
            interactive = False
            self.interactive = False

        def scan(wannabeacts):
            scannedacts = []
            if not utils.isSequence(wannabeacts):
                wannabeacts = [wannabeacts]
            for a in wannabeacts:  # scan content of list
                if isinstance(a, vtk.vtkActor):
                    scannedacts.append(a)
                    if hasattr(a, 'trail') and a.trail and not a.trail in self.actors:
                        scannedacts.append(a.trail)
                elif isinstance(a, vtk.vtkAssembly):
                    scannedacts.append(a)
                    if a.trail and not a.trail in self.actors:
                        scannedacts.append(a.trail)
                elif isinstance(a, vtk.vtkActor2D):
                    scannedacts.append(a)
                elif isinstance(a, vtk.vtkImageActor):
                    scannedacts.append(a)
                elif isinstance(a, vtk.vtkVolume):
                    scannedacts.append(a)
                elif isinstance(a, vtk.vtkImageData):
                    scannedacts.append(Volume(a))
                elif isinstance(a, vtk.vtkPolyData):
                    scannedacts.append(Actor(a, c, alpha, wire, bc))
                elif isinstance(a, str):  # assume a filepath was given
                    out = vtkio.load(a, c, alpha, wire, bc)
                    if isinstance(out, str):
                        colors.printc("~times File not found:", out, c=1)
                        scannedacts.append(None)
                    else:
                        scannedacts.append(out)
                elif "dolfin" in str(type(a)):  # assume a dolfin.Mesh object
                    from vtkplotter.dolfin import MeshActor
                    out = MeshActor(a, c=c, alpha=alpha, wire=True, bc=bc)
                    scannedacts.append(out)
                elif a is None:
                    pass
                elif isinstance(a, vtk.vtkUnstructuredGrid):
                    gf = vtk.vtkGeometryFilter()
                    gf.SetInputData(a)
                    gf.Update()
                    scannedacts.append(Actor(gf.GetOutput(), c, alpha, wire, bc))
                elif isinstance(a, vtk.vtkStructuredGrid):
                    gf = vtk.vtkGeometryFilter()
                    gf.SetInputData(a)
                    gf.Update()
                    scannedacts.append(Actor(gf.GetOutput(), c, alpha, wire, bc))
                elif isinstance(a, vtk.vtkRectilinearGrid):
                    gf = vtk.vtkRectilinearGridGeometryFilter()
                    gf.SetInputData(a)
                    gf.Update()
                    scannedacts.append(Actor(gf.GetOutput(), c, alpha, wire, bc))
                elif isinstance(a, vtk.vtkMultiBlockDataSet):
                    for i in range(a.GetNumberOfBlocks()):
                        b =  a.GetBlock(i)
                        if isinstance(b, vtk.vtkPolyData):
                            scannedacts.append(Actor(b, c, alpha, wire, bc))
                        elif isinstance(b, vtk.vtkImageData):
                            scannedacts.append(Volume(b))
                else:
                    colors.printc("~!? Cannot understand input in show():", type(a), c=1)
                    scannedacts.append(None)
            return scannedacts

        if len(actors) == 0:
            actors = None
        elif len(actors) == 1:
            actors = actors[0]
        else:
            actors = utils.flatten(actors)

        if actors is not None:
            self.actors = []
            actors2show = scan(actors)
            for a in actors2show:
                if a not in self.actors:
                    self.actors.append(a)
        else:
            actors2show = scan(self.actors)
            self.actors = list(actors2show)

        if axes is not None:
            self.axes = axes

        if interactive is not None:
            self.interactive = interactive

        if at is None and len(self.renderers) > 1:
            # in case of multiple renderers a call to show w/o specifing
            # at which renderer will just render the whole thing and return
            if self.interactor:
                if zoom:
                    self.camera.Zoom(zoom)
                self.interactor.Render()
                if self.interactive:
                    self.interactor.Start()
                return

        if at is None:
            at = 0

        if at < len(self.renderers):
            self.renderer = self.renderers[at]
        else:
            colors.printc("~times Error in show(): wrong renderer index", at, c=1)
            return

        if not self.camera:
            self.camera = self.renderer.GetActiveCamera()

        self.camera.SetParallelProjection(self.infinity)

        if self.camThickness:
            self.camera.SetThickness(self.camThickness)

        if self.sharecam:
            for r in self.renderers:
                r.SetActiveCamera(self.camera)

        if len(self.renderers) == 1:
            self.renderer.SetActiveCamera(self.camera)

        # rendering
        for ia in actors2show:  # add the actors that are not already in scene
            if ia:
                if isinstance(ia, vtk.vtkVolume):
                    self.renderer.AddVolume(ia)
                else:
                    self.renderer.AddActor(ia)
            else:
                colors.printc("~lightning Warning: Invalid actor in actors list, skip.", c=5)
        # remove the ones that are not in actors2show
        for ia in self.getActors(at):
            if ia not in actors2show:
                self.renderer.RemoveActor(ia)

        if self.axes is not None:
            addons.addAxes()
            
        addons.addLegend()
        
        if self.showFrame and len(self.renderers) > 1:
            addons.addFrame()

        if resetcam or self.initializedIren == False:
            self.renderer.ResetCamera()

        if not self.initializedIren and self.interactor:
            self.initializedIren = True
            self.interactor.Initialize()
            self.interactor.RemoveObservers("CharEvent")

            if self.verbose and self.interactive:
                docs.onelinetip()

        self.initializedPlotter = True

        if zoom:
            self.camera.Zoom(zoom)
        if azimuth:
            self.camera.Azimuth(azimuth)
        if elevation:
            self.camera.Elevation(elevation)
        if roll:
            self.camera.Roll(roll)

        if len(viewup):
            if viewup == "x":
                viewup = [1, 0, 0]
            elif viewup == "y":
                viewup = [0, 1, 0]
            elif viewup == "z":
                viewup = [0, 0, 1]
                self.camera.Azimuth(60)
                self.camera.Elevation(30)
            self.camera.Azimuth(0.01)  # otherwise camera gets locked
            self.camera.SetViewUp(viewup)

        self.renderer.ResetCameraClippingRange()

        self.window.Render()

        scbflag = False
        for a in self.actors:
            if (
                hasattr(a, "scalarbar")
                and a.scalarbar is not None
                and utils.isSequence(a.scalarbar)
            ):
                if len(a.scalarbar) == 5:  # addScalarBar
                    s1, s2, s3, s4, s5 = a.scalarbar
                    sb = self.addScalarBar(a, s1, s2, s3, s4, s5)
                    scbflag = True
                    a.scalarbar = sb  # save scalarbar actor
                elif len(a.scalarbar) == 10:  # addScalarBar3D
                    s0, s1, s2, s3, s4, s5, s6, s7, s8 = a.scalarbar
                    sb = self.addScalarBar3D(a, at, s0, s1, s2, s3, s4, s5, s6, s7, s8)
                    scbflag = True
                    a.scalarbar = sb  # save scalarbar actor
        if scbflag:
            self.window.Render()

        if settings.allowInteraction and not self.offscreen:
            self.allowInteraction()

        if settings.interactorStyle is not None:
            interactorStyle = settings.interactorStyle

        if interactorStyle == 0 or interactorStyle == "TrackballCamera":
            pass  # do nothing
        elif interactorStyle == 1 or interactorStyle == "TrackballActor":
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballActor())
        elif interactorStyle == 2 or interactorStyle == "JoystickCamera":
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleJoystickCamera())
        elif interactorStyle == 3 or interactorStyle == "Unicam":
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleUnicam())
        elif interactorStyle == 4 or interactorStyle == "Flight":
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleFlight())
        elif interactorStyle == 5 or interactorStyle == "RubberBand3D":
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleRubberBand3D())
        elif interactorStyle == 6 or interactorStyle == "RubberBandZoom":
            self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleRubberBandZoom())

        if self.interactor and self.interactive:
            self.interactor.Start()

        if rate:
            if self.clock is None:  # set clock and limit rate
                self._clockt0 = time.time()
                self.clock = 0.0
            else:
                t = time.time() - self._clockt0
                elapsed = t - self.clock
                mint = 1.0 / rate
                if elapsed < mint:
                    time.sleep(mint - elapsed)
                self.clock = time.time() - self._clockt0

        if q:  # gracefully exit
            if self.verbose:
                print("q flag set to True. Exit.")
            sys.exit(0)

    def lastActor(self):
        """Return last added ``Actor``."""
        return self.actors[-1]

    def removeActor(self, a):
        """Remove ``vtkActor`` or actor index from current renderer."""
        if not self.initializedPlotter:
            save_int = self.interactive
            self.show(interactive=0)
            self.interactive = save_int
            return
        if self.renderer:
            self.renderer.RemoveActor(a)
        if a in self.actors:
            i = self.actors.index(a)
            del self.actors[i]

    def clear(self, actors=()):
        """Delete specified list of actors, by default delete all."""
        if not utils.isSequence(actors):
            actors = [actors]
        if len(actors):
            for a in actors:
                self.removeActor(a)
        else:
            settings.collectable_actors = [] 
            self.actors = []
            for a in self.getActors():
                self.renderer.RemoveActor(a)
            for s in self.sliders:
                s.EnabledOff()
            for b in self.buttons:
                self.renderer.RemoveActor(b)
            for w in self.widgets:
                w.EnabledOff()
            for c in self.scalarbars:
                self.renderer.RemoveActor(c)
