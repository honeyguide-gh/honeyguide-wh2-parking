import json
tpl = open('viewer.html').read()
out = (tpl.replace('__SCENE__', open('out/scene.json').read())
          .replace('__MESH_HG3__', open('hg3_mesh.json').read())
          .replace('__MESH_HGF__', open('hgf_mesh.json').read())
          .replace('__MESH__', open('trike_mesh.json').read()))
open('out/wh2-parking.html', 'w').write(out)
print(f"{len(out)/1024:.0f} kB")
