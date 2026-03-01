(function () {
  'use strict';

  var container = document.getElementById('process-3d-canvas');
  if (!container || typeof THREE === 'undefined') return;

  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0a0b);
  scene.fog = new THREE.FogExp2(0x0a0a0b, 0.012);

  var w = container.clientWidth || 800;
  var h = container.clientHeight || 320;
  var camera = new THREE.PerspectiveCamera(28, w / h, 0.1, 100);
  camera.position.set(0, 1.2, 5.5);
  camera.lookAt(0, 0.2, 0);

  var renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(w, h);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  if (renderer.outputColorSpace !== undefined) renderer.outputColorSpace = THREE.SRGBColorSpace;
  else if (renderer.outputEncoding !== undefined) renderer.outputEncoding = THREE.sRGBEncoding;
  container.appendChild(renderer.domElement);

  var accent = 0xE98733;
  var carGroup = new THREE.Group();

  var bodyMat = new THREE.MeshStandardMaterial({
    color: accent,
    metalness: 0.5,
    roughness: 0.4,
  });
  var body = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.35, 0.55), bodyMat);
  body.position.y = 0.2;
  body.castShadow = true;
  carGroup.add(body);

  var cabinMat = new THREE.MeshStandardMaterial({
    color: 0x1a1a1a,
    metalness: 0.6,
    roughness: 0.35,
  });
  var cabin = new THREE.Mesh(new THREE.BoxGeometry(0.75, 0.4, 0.5), cabinMat);
  cabin.position.set(0, 0.5, 0);
  cabin.castShadow = true;
  carGroup.add(cabin);

  var wheelMat = new THREE.MeshStandardMaterial({
    color: 0x222222,
    metalness: 0.8,
    roughness: 0.3,
  });
  var wheelGeom = new THREE.CylinderGeometry(0.15, 0.15, 0.08, 16);
  var fl = new THREE.Mesh(wheelGeom, wheelMat);
  fl.rotation.z = Math.PI / 2;
  fl.position.set(-0.5, 0.15, 0.32);
  carGroup.add(fl);
  var fr = new THREE.Mesh(wheelGeom, wheelMat);
  fr.rotation.z = Math.PI / 2;
  fr.position.set(0.5, 0.15, 0.32);
  carGroup.add(fr);
  var rl = new THREE.Mesh(wheelGeom, wheelMat);
  rl.rotation.z = Math.PI / 2;
  rl.position.set(-0.5, 0.15, -0.32);
  carGroup.add(rl);
  var rr = new THREE.Mesh(wheelGeom, wheelMat);
  rr.rotation.z = Math.PI / 2;
  rr.position.set(0.5, 0.15, -0.32);
  carGroup.add(rr);

  carGroup.rotation.y = Math.PI / 6;
  scene.add(carGroup);

  var ambient = new THREE.AmbientLight(0x404060, 0.8);
  scene.add(ambient);
  var key = new THREE.DirectionalLight(0xffffff, 0.9);
  key.position.set(3, 4, 5);
  scene.add(key);
  var fill = new THREE.DirectionalLight(0xE98733, 0.25);
  fill.position.set(-2, 1, 2);
  scene.add(fill);

  var clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    var t = clock.getElapsedTime();
    carGroup.rotation.y = Math.PI / 6 + t * 0.15;
    renderer.render(scene, camera);
  }
  animate();

  function onResize() {
    var w = container.clientWidth;
    var h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }
  window.addEventListener('resize', onResize);
})();
