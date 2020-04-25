# Circuit Markup v0.1

Circuit Markup is a markup langauge for generating electric circuit schematics in SVG.

**BE WARNED!** I am skeptical of calling this even v0.1 - it is in no way usable except for a very limited set of use cases. That being said, I am looking forward to extending it more and more, so that one day you can use Circuit Markup as *the default* when drawing schematics.

## Motivation

Currently there are a fair number of tools, both GUI and text-based, that are used for drawing circuit schematics. The ones I know of are:

- KiCAD
- gEDA
- xcircuit
- circuitikz

Of those, all except circuitikz are GUI based. The problems with them are that

- **they don't generate pretty schematics** - KiCAD and gEDA are used more for actual engineering, instead of drawing schematics to be published/printed.
- **they are hard to use** - maybe it's because I've been programming for so long, but I feel very unproductive when using GUI tools, compared to text based and/or command-line based solutions.

On the other hand, circuitikz is made exactly for generating pretty schematics designed to be published/printed, *however*....it's implemented in LaTeX. I am going to be upfront about this:

**I DO NOT LIKE LATEX!**

I respect it as a piece of software, I accept that it is used by a lot of people and does the job™. **That being said**, I believe it is excruciatingly hard to use and 10 orders of magnitude harder to understand.

The reason I started this project is because I want to make a program where you give it some very simplisitc text input, that anyone can read and understand, and it spits out a very simplisitc circuit diagram that anyone can appreciate in quality. After that, you can do whatever you want with it. This also aligns with the UNIX philosophy (which I respect very much), that is: do one thing and do it well.

Now that we're done with the preface, I invite you to run `make examples` and see the source and results in the `examples` directory. At this point in time, Circuit Markup is a very simple markup language, so it should be sufficiently easy to understand by reading the example sources. However, if you think that this is not the case, feel free to open an issue and/or provide more documentation yourself!
