import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { RenderPass } from "three/examples/jsm/postprocessing/RenderPass.js";
import { EffectComposer } from "three/examples/jsm/postprocessing/EffectComposer.js";
import { GammaCorrectionShader } from "three/examples/jsm/shaders/GammaCorrectionShader.js";
import { ShaderPass } from "three/examples/jsm/postprocessing/ShaderPass.js";
import { RGBShiftShader } from "three/examples/jsm/shaders/RGBShiftShader.js";

const TEXTURE_PATH = "https://res.cloudinary.com/dg5nsedzw/image/upload/v1641657168/blog/vaporwave-threejs-textures/grid.png";
const DISPLACEMENT_PATH = "https://res.cloudinary.com/dg5nsedzw/image/upload/v1641657200/blog/vaporwave-threejs-textures/displacement.png";
const METALNESS_PATH = "https://res.cloudinary.com/dg5nsedzw/image/upload/v1641657200/blog/vaporwave-threejs-textures/metalness.png";

// Textures
const textureLoader = new THREE.TextureLoader();
const gridTexture = textureLoader.load(TEXTURE_PATH);
const terrainTexture = textureLoader.load(DISPLACEMENT_PATH);
const metalnessTexture = textureLoader.load(METALNESS_PATH);

let effectComposer, vaporPlane, vaporPlane2, vaporPlane3;

export function initVaporwaveScene(scene, camera, renderer, sizes) {
  // Fog so you dont see the end of the plane
const fog = new THREE.Fog("#000000", 1, 60);
scene.fog = fog;

  // Objects
  const geometry = new THREE.PlaneGeometry(20, 40, 24, 24); //original values x20
  const material = new THREE.MeshStandardMaterial({
    map: gridTexture,
    displacementMap: terrainTexture,
    displacementScale: 8,
    metalnessMap: metalnessTexture,
    metalness: 0.96,
    roughness: 0.5,
  });

  vaporPlane = new THREE.Mesh(geometry, material);
  vaporPlane.rotation.x = -Math.PI * 0.5;
  vaporPlane.position.y = 0.0;
  vaporPlane.position.z = 3;

  vaporPlane2 = new THREE.Mesh(geometry, material);
  vaporPlane2.rotation.x = -Math.PI * 0.5;
  vaporPlane2.position.y = 0.0;
  vaporPlane2.position.z = -37; // 0.15 - 2 (the length of the first vaporPlane)

  vaporPlane3 = new THREE.Mesh(geometry, material);
  vaporPlane3.rotation.x = -Math.PI * 0.5;
  vaporPlane3.position.y = 0.0;
  vaporPlane3.position.z = 43;

  scene.add(vaporPlane);
  scene.add(vaporPlane2);
  scene.add(vaporPlane3);

  // Post Processing
  effectComposer = new EffectComposer(renderer);
  effectComposer.setSize(sizes.width, sizes.height);
  effectComposer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

  const renderPass = new RenderPass(scene, camera);
  effectComposer.addPass(renderPass);

  const rgbShiftPass = new ShaderPass(RGBShiftShader);
  rgbShiftPass.uniforms["amount"].value = 0.0015;
  effectComposer.addPass(rgbShiftPass);

  const gammaCorrectionPass = new ShaderPass(GammaCorrectionShader);
  effectComposer.addPass(gammaCorrectionPass);
}

export { vaporPlane, vaporPlane2, vaporPlane3, effectComposer };
