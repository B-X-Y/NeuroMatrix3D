import * as THREE from "three";
import {STLLoader} from "three/addons/loaders/STLLoader.js";
import {OrbitControls} from "three/addons/controls/OrbitControls.js";

const config = window.STL_VIEWER_CONFIG || {};
const stlUrl = config.stlUrl;

const viewer = document.getElementById("viewer");
const loading = document.getElementById("loading");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf5f5f5);

const camera = new THREE.PerspectiveCamera(
    45,
    window.innerWidth / window.innerHeight,
    0.1,
    100000
);

const renderer = new THREE.WebGLRenderer({antialias: true});
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
viewer.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 2));

const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
directionalLight.position.set(1, -1, 2);
scene.add(directionalLight);

const material = new THREE.MeshStandardMaterial({
    color: 0x888888,
    roughness: 0.6,
    metalness: 0.05
});

const loader = new STLLoader();

loader.load(
    stlUrl,
    geometry => {
        geometry.computeVertexNormals();
        geometry.center();

        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        const box = new THREE.Box3().setFromObject(mesh);
        const size = box.getSize(new THREE.Vector3()).length();

        camera.position.set(size, -size, size);
        camera.near = size / 1000;
        camera.far = size * 1000;
        camera.updateProjectionMatrix();

        controls.target.set(0, 0, 0);
        controls.update();

        loading.style.display = "none";
    },
    xhr => {
        if (xhr.lengthComputable) {
            const percent = Math.round((xhr.loaded / xhr.total) * 100);
            loading.textContent = `Loading model... ${percent}%`;
        }
    },
    error => {
        console.error(error);
        loading.textContent = "Failed to load model";
    }
);

window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

animate();
