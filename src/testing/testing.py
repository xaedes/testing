#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from funcy import decorator
from copy import copy
import numpy as np
import glob
import os
import operator

####################################################################################
####################################################################################
##            ######################################################################
## generators ######################################################################
##            ######################################################################
####################################################################################
####################################################################################


def generateNaturalIntegers():
    '''
    @summary: generator for natural integers (0,1,...,infinity)
    @result: sequence 0,1,...,infinity
    '''
    k = 0
    while True:
        yield k
        k += 1

def generateIntegersSignSwitching():
    '''
    @summary: generator for signed integers with ascending magnitude (0,1,-1,2,-2,3,-3,...)
    @result: sequence 0,1,-1,2,-2,3,-3,...
    '''
    yield 0
    k = 1
    while True:
        yield k
        yield -k
        k += 1

def generateRandomNormals(mean,std):
    '''
    @summary: generator for random normal values
    @param mean: mean of random normal variable
    @param std:  std of random normal variable
    @result: sequence e0,e1,e2,e3,...
                 where e_i is drawn from Normal(mean,std)
    '''
    while True:
        yield float(np.random.normal(mean,std))

def generateUniformRandoms(min,max):
    '''
    @summary: generator for uniform random values e in [min..max]
    @param min: 
    @param max: 
    @result: sequence e0,e1,e2,e3,...
                 where e_i is drawn from [min..max]
    '''
    while True:
        yield float(np.random.uniform(min,max))

def generateSubSequences(iterator):
    '''
    @summary:        generator for subsequences of another iterator: it0,it1,it2,...
    @param iterator: iterator with sequence it0,it1,it2,...
    @result:         sequence [],[it0],[it0,it1],[it0,it1,it2],...
    '''
    seq = []
    while True:
        yield copy(seq)
        seq.append(iterator.next())

def generateNaturalIntegerSubSequences():
    '''
    @summary: generator for subsequences of natural integers
    @result: sequence [],[0],[0,1],[0,1,2],[0,1,2,3],...,[0,..,infinity]
    '''
    return generateSubSequences(generateNaturalIntegers())


def generateRandomNormalSubSequences(mean,std):
    '''
    @summary: generator for subsequences of random normal values
    @param mean: mean of random normal variable
    @param std:  std of random normal variable
    @result: sequence [],[e0],[e0,e1],[e0,e1,e2],[e0,e1,e2,e3],...,
                 where e_i is drawn from Normal(mean,std)
    '''
    return generateSubSequences(generateRandomNormals(mean,std))


####################################################################################
####################################################################################
##            ######################################################################
## decorators ######################################################################
##            ######################################################################
####################################################################################
####################################################################################

def forEach(parameter_name, generator, n=None):
    '''
    Usage:
    @forEach("i", generateNaturalInteger, 10)
    def square(self, x):
        return x*x
    assert square() == [x*x for x in range(10)]
    
    @forEach("i", lambda:iter(range(10)))
    def square(self, x):
        return x*x
    assert square() == [x*x for x in range(10)]

    @summary:              decorator that applies n values from generator to parameter_name of function and collect results
    @param parameter_name: which (named) parameter in function to set
    @param generator:      function with zero arguments that returns iterator object
    @param n[=None]:       how many values to take from generator, if None, take values until StopIteration occurs
    @result:               
    '''
    def outer(function):
        def wrap(*args,**kwargs):
            result = {
                "parameter_name":parameter_name,
                "parameter_values":[],
                "results":[]
            }
            it = generator()
            i = 0
            while n is None or i < n:
                try:
                    kwargs[parameter_name] = it.next()
                except StopIteration:
                    return result
                result["parameter_values"].append(kwargs[parameter_name])
                result["results"].append(function(*args,**kwargs))
                i += 1

            return result
        return wrap

    return outer

def useParameters(parameter_name, input_parameter_names, func, star=True, consume=True):
    '''
    Usage:
    @forEach("w",lambda:generateNaturalIntegers,10)
    @forEach("h",lambda:generateNaturalIntegers,10)
    @useParameters("arr",["w","h"],lambda w,h:np.random.normal(0,1,size=(w,h)))
    def test(arr):
        return arr.shape
    results=test()

    @summary:                      decorator that consumes values from the kwargs of the 
                                   decorated function to generate a new parameter value
    @param parameter_name:         name of the new parameter value
    @param input_parameter_names:  name of the parameters to consume
    @param func:                   function that takes consumed parameters and returns value for parameter
    @param star[=True]:            whether to use input_parameter_names as kwargs, or as normal args
    @param consume[=True]:         whether to remove used input_parameter_names from kwargs of original function call
    @result:                 
    '''
    def outer(function):
        def wrap(*args,**kwargs):
            # collect parameters and consume them
            _args = []
            _kwargs = dict()
            for key in input_parameter_names:
                if star:
                    _kwargs[key] = kwargs[key]
                else:
                    _args.append(kwargs[key])

                if consume:
                    del kwargs[key]

            # apply func to collected params
            kwargs[parameter_name] = func(*_args,**_kwargs)

            return function(*args,**kwargs)
        return wrap
    return outer

def forFiles(parameter_name, glob_pattern=None, directory=None):
    '''
    Usage:
    @forFile("fn","data/*.csv",os.path.dirname(__file__))
    def process_csv(fn):
        ...
    results=process_csv()


    @summary:              decorator that popoluates a parameter with files from directory that matched glob pattern
    @param parameter_name: 
    @param glob_pattern:
    @param directory:
    @result: 
    '''
    def outer(function):
        def wrap(*args,**kwargs):
            if directory is not None:
                os.chdir(directory)

            result = {
                "parameter_name":parameter_name,
                "parameter_values": [],
                "results": []
            }
            # apply func to collected params
            for fn in glob.glob(glob_pattern):
                kwargs[parameter_name] = fn
                result["parameter_values"].append(fn)
                result["results"].append(function(*args,**kwargs))
            return result
        return wrap
    return outer

def mapParameter(parameter_name, map_function):
    '''
    Usage
    @mapParameter("arr",lambda arr:np.array(arr))
    def n_items(arr):
        return reduce(operator.mul, arr.shape, 1)

    assert n_items(arr=[[1,2],[3,4],[0,0]]) == 6

    @summary:              decorator that applies map_function to parameter before applying it to original function
    @param parameter_name:
    @param map_function:
    @result: 
    '''
    def outer(function):
        def wrap(*args,**kwargs):
            kwargs[parameter_name] = map_function(kwargs[parameter_name])
            return function(*args,**kwargs)
        return wrap
    return outer

def discardParameter(parameter_name):
    '''
    Usage
    @discardParameter("foo")
    def mul(a,b,**kwargs):
        assert "foo" not in kwargs
        return a*b
    mul(a=10,b=10,foo="bar")

    @summary:              decorator that removes parameter_name from kwargs of original function
    @param parameter_name:
    @result: 
    '''
    def outer(function):
        def wrap(*args,**kwargs):
            del kwargs[parameter_name]
            return function(*args,**kwargs)
        return wrap
    return outer