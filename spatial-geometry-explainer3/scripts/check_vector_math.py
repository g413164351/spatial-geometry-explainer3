#!/usr/bin/env python3
"""Domain-neutral math regression: projection, reconstruction, rotation, angles.

Tests an independent reference implementation, not any generated HTML.
No aerodynamic or other application-specific equations are bundled.
"""
from math import atan2, cos, sin, pi, sqrt, isclose
from random import Random


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def add(a,b):
    return tuple(x+y for x,y in zip(a,b))


def sub(a,b):
    return tuple(x-y for x,y in zip(a,b))


def mul(a,k):
    return tuple(k*x for x in a)


def norm(a):
    return sqrt(dot(a,a))


def unit(a):
    m=norm(a)
    if m==0:
        raise ValueError("zero direction has no unit vector")
    return mul(a,1/m)


def split(v,n):
    direction=unit(n)
    along=mul(direction,dot(v,direction))
    return along,sub(v,along)


def near(a,b,atol=1e-10):
    assert all(isclose(x,y,rel_tol=1e-10,abs_tol=atol) for x,y in zip(a,b)), (a,b)


def rotate2d(v,theta):
    c,s=cos(theta),sin(theta)
    return (c*v[0]-s*v[1],s*v[0]+c*v[1])


def signed_angle2d(a,b):
    return atan2(a[0]*b[1]-a[1]*b[0],dot(a,b))


def main():
    rng=Random(101)
    for dim in (2,3):
        for _ in range(300):
            v=tuple(rng.uniform(-100,100) for _ in range(dim))
            n=tuple(rng.uniform(-3,3) for _ in range(dim))
            a,r=split(v,n)
            near(add(a,r),v)
            assert abs(dot(r,unit(n)))<1e-9
            a2,r2=split(v,mul(n,-1))
            near(a,a2)    # signed scalar changes, projection vector doesn't
            near(r,r2)
            a3,r3=split(mul(v,-1),n)
            near(a3,mul(a,-1))
            near(r3,mul(r,-1))
    for theta in (-pi,-2.3,-1.1,-.05,0,.05,1.1,2.3,pi):
        p=(3.5,-1.25)
        moved=rotate2d(p,theta)
        assert abs(norm(moved)-norm(p))<1e-10
        near(rotate2d(moved,-theta),p)
        if -pi<theta<pi:
            assert abs(signed_angle2d(p,moved)-theta)<1e-10
    z=(0,0,0)
    a,r=split(z,(0,0,1))
    near(a,z)
    near(r,z)
    try:
        unit(z)
        raise AssertionError("zero direction should raise")
    except ValueError:
        pass
    print("PASS: generic 2D/3D dot projection, orthogonality and reconstruction")
    print("PASS: direction sign, input sign, zero input and zero direction")
    print("PASS: rotation length preservation, inverse rotation, signed angle")
    print("LIMIT: domain-specific physics and rendered diagrams require separate checks")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
