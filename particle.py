import numpy as np

SUN_POS = np.array([0.0, 0.0, 0.0], dtype=np.float32)
EARTH_POS = np.array([40.0, 0.0, 0.0], dtype=np.float32)

SUN_RADIUS = 10.9
EARTH_RADIUS = 1.0
INTERACTION_RADIUS = 3.0


class ParticleSystem:
    def __init__(self, count=1200):
        self.count = count
        self.positions = np.zeros((count, 3), dtype=np.float32)
        self.velocities = np.zeros((count, 3), dtype=np.float32)
        self.intensities = np.ones(count, dtype=np.float32)
        self.colors = np.ones((count, 3), dtype=np.float32)
        self.states = np.zeros(count, dtype=np.int32)
        self.life = np.zeros(count, dtype=np.float32)
        self.emission_scale = 1.0
        self.reset_all()

    def set_emission_scale(self, scale):
        self.emission_scale = scale

    def random_point_on_sun_toward_earth(self):
        # 태양 중심에서 지구 방향
        earth_dir = EARTH_POS - SUN_POS
        earth_dir = earth_dir / np.linalg.norm(earth_dir)

        # 지구 방향 반구에서만 파티클 생성
        while True:
            direction = np.random.normal(size=3)
            direction = direction / np.linalg.norm(direction)

            if np.dot(direction, earth_dir) > 0.2:
                return SUN_POS + direction * SUN_RADIUS

    def reset_particle(self, i):
        start = self.random_point_on_sun_toward_earth()

        direction_to_earth = EARTH_POS - start
        direction_to_earth = direction_to_earth / np.linalg.norm(direction_to_earth)

        noise = np.random.normal(scale=0.04, size=3)
        direction = direction_to_earth + noise
        direction = direction / np.linalg.norm(direction)

        speed = np.random.uniform(8.0, 14.0)

        self.positions[i] = start
        self.velocities[i] = direction * speed
        self.intensities[i] = self.emission_scale
        self.colors[i] = np.array([1.0, 0.85, 0.2], dtype=np.float32)
        self.states[i] = 0
        self.life[i] = 0.0

    def reset_all(self):
        for i in range(self.count):
            self.reset_particle(i)

    def interact_with_earth(self, i):
        rand = np.random.rand()

        normal = self.positions[i] - EARTH_POS
        normal = normal / np.linalg.norm(normal)

        incoming = self.velocities[i]
        incoming = incoming / np.linalg.norm(incoming)

        if rand < 0.5:
            self.states[i] = 1
            self.velocities[i] = np.array([0.0, 0.0, 0.0], dtype=np.float32)
            self.colors[i] = np.array([1.0, 0.25, 0.15], dtype=np.float32)

        elif rand < 0.8:
            self.states[i] = 2
            reflected = incoming - 2.0 * np.dot(incoming, normal) * normal
            self.velocities[i] = reflected * np.random.uniform(5.0, 9.0)
            self.colors[i] = np.array([0.4, 0.9, 1.0], dtype=np.float32)

        else:
            self.states[i] = 3
            scatter = normal + np.random.normal(scale=0.8, size=3)
            scatter = scatter / np.linalg.norm(scatter)
            self.velocities[i] = scatter * np.random.uniform(3.0, 7.0)
            self.colors[i] = np.array([0.7, 0.4, 1.0], dtype=np.float32)

        self.life[i] = 0.0

    def update(self, dt):
        self.positions += self.velocities * dt
        self.life += dt

        # 너무 어두워지지 않게 고정
        self.intensities = np.full(self.count, self.emission_scale, dtype=np.float32)

        distances_from_sun = np.linalg.norm(self.positions - SUN_POS, axis=1)
        distances_from_earth = np.linalg.norm(self.positions - EARTH_POS, axis=1)

        moving = self.states == 0
        hit_earth = (distances_from_earth < INTERACTION_RADIUS) & moving

        for i in np.where(hit_earth)[0]:
            self.interact_with_earth(i)

        too_far = distances_from_sun > 90.0
        dead_after_interaction = (self.states != 0) & (self.life > 2.0)

        reset_mask = too_far | dead_after_interaction

        for i in np.where(reset_mask)[0]:
            self.reset_particle(i)

    def get_positions(self):
        return self.positions.astype(np.float32)

    def get_intensities(self):
        return self.intensities.astype(np.float32)

    def get_colors(self):
        return self.colors.astype(np.float32)