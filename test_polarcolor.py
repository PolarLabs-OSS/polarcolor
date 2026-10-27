from polarcolor import normalize,rgb,hsl,from_rgb
assert normalize('abc')=='#AABBCC'
assert rgb('#FF0000')==(255,0,0)
assert hsl('#FF0000')==(0,100,50)
assert from_rgb(0,128,255)=='#0080FF'
for invalid in ('#xyz','#12345','red'):
    try: normalize(invalid);raise AssertionError('Expected error')
    except ValueError: pass
print('PASS: HEX, RGB, HSL, input validation')
