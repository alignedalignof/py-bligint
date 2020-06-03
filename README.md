py-bligint
==========

Program to test algorithmical complexities of big integer arithmetic.
Specifically, measures the time to raise a large integer to some power.


| Multiplication    | Number                            | Time, s           
| ---               |:---                               |:---               
| Halfwise          | 9876543210987654321^200           | 111
| Karatsuba         | 9876543210987654321^200           | 61.5
| Digitwise + cache | 9876543210987654321^**600**       | 20.3
| Py native         | 9876543210987654321^**20000**     | 1.28

Unsuprisingly built-in native big integer performance is exceedingly greater
than anything written in pure Python. What is interesting, digitwise
multiplication with a straightforward caching mechanism performed well.
