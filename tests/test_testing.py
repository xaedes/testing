#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import division

import pytest
import os
import numpy as np
from testing import *
from itertools import islice,chain
import operator
from funcy import partial

class TestTesting():
    def test_generateNaturalIntegers(self):
        assert list(islice(generateNaturalIntegers(),10)) == list(range(10))
        for i in islice(generateNaturalIntegers(),10):
            assert type(i) == int
        
    def test_generateNaturalIntegerSubSequences(self):
        assert list(islice(generateNaturalIntegerSubSequences(),5)) == [[],[0],[0,1],[0,1,2],[0,1,2,3]]
    
    def test_generateRandomNormalSubSequences(self):
        result = list(islice(generateRandomNormalSubSequences(0,1),5))
        for i in range(5):
            assert len(result[i]) == i
            for j in range(i-1):
                for k in range(1,j-1):
                    print i,j,k
                    assert result[i][j] == result[k][j]

    def test_generateRandomNormals(self):
        for f in islice(generateRandomNormals(0,1),10):
            assert type(f) == float

    def test_generateUniformRandoms(self):
        for f in islice(generateUniformRandoms(0,1),10):
            assert type(f) == float
            assert f >= 0
            assert f <= 1

    def test_generateIntegersSignSwitching(self):
        correct = [0,1,-1,2,-2,3,-3]
        assert list(islice(generateIntegersSignSwitching(),len(correct))) == correct

    @forEach("lst",lambda:chain(iter([list(range(10))]),generateNaturalIntegerSubSequences()),10)
    def test_generateSubSequences_lists(self,lst):
        n = len(lst)
        result = list(islice(generateSubSequences(iter(lst)), n))
        for i in range(n):
            assert result[i] == lst[:i]


    def test_forEach_CatchStopIteration(self):

        @forEach("a",lambda:iter([]),10)
        def func(a):
            return a

        func()

    def test_forEach(self):

        @forEach("a",generateNaturalIntegers,10)
        def func(a):
            return a+1
        
        result = func()
        assert result["parameter_name"]=="a"
        for i in range(10):
            assert result["parameter_values"][i] == i
            assert result["results"][i] == i+1


    def test_forEach_nested1(self):

        @forEach("a",generateNaturalIntegers,10)
        @forEach("b",generateNaturalIntegers,10)
        def func(a,b):
            return a*b
        
        result = func()
        print result
        assert result["parameter_name"]=="a"
        for a in range(10):
            assert result["results"][a]["parameter_name"]=="b"
            for b in range(10):
                assert result["results"][a]["results"][b] == a*b


    def test_forEach_nested2(self):

        @forEach("a",generateNaturalIntegers,10)
        @forEach("b",lambda:iter(['x','y']),10)
        def func(a,b):
            return a*b
        
        result = func()
        print result
        assert result["parameter_name"]=="a"
        for ia,a in enumerate(range(10)):
            assert result["results"][ia]["parameter_name"]=="b"
            for ib,b in enumerate(['x','y']):
                assert result["results"][ia]["results"][ib] == a*b

    def test_forEach_n_is_None(self):

        @forEach("a",lambda:iter(range(5)))
        def func(a):
            return a+1

        result = func()
        for a in range(5):
            assert a in result["parameter_values"]
            assert a+1 == result["results"][a]

        assert 5 not in result["parameter_values"]
        assert 5 in result["results"]

    @forEach("a",generateNaturalIntegers,10)
    @forEach("b",generateNaturalIntegers,10)
    def test_useParameters(self,a,b):
        @useParameters("c",["a","b"],lambda a,b:a*b)
        def mul(c):
            return c

        assert mul(a=a,b=b) == a*b

        @useParameters("c",["a","b"],lambda a,b:a+b)
        def add(c):
            return c

        assert add(a=a,b=b) == a+b

    def test_useParameters2(self):

        @useParameters("c",["a","b"],lambda a,b:a*b)
        def mul(c):
            return c

        assert mul(a=10,b=10) == 100
        assert mul(a=10,b=10,c=0) == 100 

        @useParameters("c",["a","b"],lambda a,b:a+b)
        def add(c, z):
            return c + z

        assert add(a=10,b=10,c=0,z=5) == 25
        assert add(a=10,b=10,c=100,z=5) == 25

    def test_useParameters_missing_consumed_params_exception(self):
        @useParameters("c",["a","b"],lambda a,b:a*b,consume=True)
        def mul(c):
            return c

        with pytest.raises(KeyError):
            mul(c=10) # a and b are missing
        with pytest.raises(KeyError):
            mul(a=10) # b is missing
        with pytest.raises(KeyError):
            mul(b=10) # a is missing

    def test_useParameters_missing_params_in_original_function_exception(self):
        @useParameters("c",["a","b"],lambda a,b:a+b)
        def add(c, z):
            return c + z

        with pytest.raises(TypeError):
            # z is missing
            add(a=10,b=10)
            add(a=10,b=10,c=100)

    def test_useParameters_missing_kwargs_in_func_exception(self):

        @useParameters("c",["a","b"],lambda d,e:d*e)
        def mul(c):
            return c

        with pytest.raises(TypeError):
            mul(a=10,b=10)
        with pytest.raises(TypeError):
            mul(a=10,b=10,d=10)
        with pytest.raises(TypeError):
            mul(a=10,b=10,e=10)

    def test_useParameters_star_default(self):
        @useParameters("c",["a","b"],lambda x,y:x*y)
        def mul(c):
            return c
        with pytest.raises(TypeError):
            mul(a=10,b=10)

    def test_useParameters_star_true(self):
        @useParameters("c",["a","b"],lambda x,y:x*y,star=True)
        def mul(c):
            return c
        with pytest.raises(TypeError):
            mul(a=10,b=10)

    def test_useParameters_star_false(self):
        @useParameters("c",["a","b"],lambda x,y:x*y,star=False)
        def mul(c):
            return c
        assert mul(a=10,b=10) == 100

    def test_useParameters_consume_default(self):
        @useParameters("c",["a","b"],lambda a,b:a*b,consume=True)
        def mul(c,a,b):
            return c-a+b
        with pytest.raises(TypeError):
            mul(a=10,b=10)

    def test_useParameters_consume_true(self):
        @useParameters("c",["a","b"],lambda a,b:a*b,consume=True)
        def mul(c,a,b):
            return c-a+b
        with pytest.raises(TypeError):
            mul(a=10,b=10)

    @forEach("a",partial(generateRandomNormals,0,1),10)
    @forEach("b",partial(generateRandomNormals,0,1),10)
    def test_useParameters_consume_false(self,a,b):
        @useParameters("c",["a","b"],lambda a,b:a*b,consume=False)
        def mul(c,a,b):
            return c-a+b
        assert mul(a=a,b=b) == a*b-a+b

    def test_forFiles1(self):
        dirname = os.path.dirname(__file__)
        basename = os.path.basename(__file__)
        name,ext = os.path.splitext(basename)
        @forFiles("fn", glob_pattern=name+"*", directory=dirname)
        def test(fn):
            return fn

        result = test()
        assert result["parameter_name"] == "fn"
        assert basename in result["parameter_values"]
        assert basename in result["results"]


    def test_forFiles2(self):
        dirname = os.path.dirname(__file__)
        basename = os.path.basename(__file__)
        name,ext = os.path.splitext(basename)
        @forFiles("fn", glob_pattern="*"+ext, directory=dirname)
        def test(fn):
            return fn

        result = test()
        assert result["parameter_name"] == "fn"
        assert basename in result["parameter_values"]
        assert basename in result["results"]

    def test_forFiles3(self):
        dirname = os.path.dirname(__file__)
        basename = os.path.basename(__file__)
        @forFiles("fn", glob_pattern="*"+str(np.random.normal(0,1))+"*", directory=dirname)
        def test(fn):
            return fn

        result = test()
        assert result["parameter_name"] == "fn"
        assert basename not in result["parameter_values"]
        assert basename not in result["results"]

    def test_forFiles4(self):
        dirname = os.path.dirname(__file__)
        @forFiles("fn", glob_pattern="*", directory=dirname)
        def test(fn):
            return fn

        result = test()
        assert result["parameter_name"] == "fn"
        assert "." not in result["parameter_values"]
        assert "." not in result["results"]
        assert ".." not in result["parameter_values"]
        assert ".." not in result["results"]

    def test_mapParameter_working1(self):
        arr = [[1,2],[3,4],[0,0]]
        @mapParameter("arr",np.array)
        def arr_type(arr):
            return type(arr)

        assert arr_type(arr=arr) == np.ndarray
        
    def test_mapParameter_working2(self):
        arr = [[1,2],[3,4],[0,0]]
        @mapParameter("arr",lambda arr:np.array(arr))
        def arr_type(arr):
            return type(arr)

        assert arr_type(arr=arr) == np.ndarray

    def test_mapParameter_exceptions(self):
        arr = [[1,2],[3,4],[0,0]]
        @mapParameter("unused",lambda unused:np.array(arr))
        def arr_type(arr):
            return type(arr)

        with pytest.raises(KeyError):
            arr_type(arr=arr)
        with pytest.raises(TypeError):
            arr_type(unused=arr)

    def test_mapParameter_map_function_no_kwarg(self):
        arr = [[1,2],[3,4],[0,0]]
        @mapParameter("foo",lambda bar:np.array(arr))
        def arr_type(foo):
            return type(foo)

        assert arr_type(foo=arr) == np.ndarray


    def test_discardParameter(self):

        @discardParameter("foo")
        def func(*args,**kwargs):
            assert "foo" not in kwargs

        func(foo="bar")
                