import taichi as ti
import numpy as np
import time
import pygame
from sys import exit
import moderngl
import glm 

#setup
ti.init(arch=ti.gpu)
pygame.init()
WIDTH, HEIGHT = 1000, 1000
print("GL Version:",
      pygame.display.gl_get_attribute(
          pygame.GL_CONTEXT_MAJOR_VERSION
      ),
      pygame.display.gl_get_attribute(
          pygame.GL_CONTEXT_MINOR_VERSION
      ))
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption("N-Body Simulation")
ctx = moderngl.create_context(require=330)
ctx.enable(moderngl.BLEND)
ctx.enable(moderngl.PROGRAM_POINT_SIZE)
ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA)

@ti.data_oriented
class Simulation:
    def __init__(self):
        self.max_bodies = 50000
        self.positions = ti.Vector.field(3, dtype=ti.f32, shape=self.max_bodies)
        self.velocities = ti.Vector.field(3, dtype=ti.f32, shape=self.max_bodies)
        self.accelerations = ti.Vector.field(3, dtype=ti.f32, shape=self.max_bodies)

        self.masses = ti.field(dtype=ti.i32, shape=self.max_bodies)

        self.active_bodies = ti.field(dtype=ti.i32, shape=())
        self.active_bodies[None] = 0

        self.G = 5
        self.dt = 1/60

    @ti.kernel
    def init_particles(self, num_bodies: ti.i32):
        for i in range(num_bodies):
            self.positions[i] = [
                ti.random() * WIDTH / 4,
                ti.random() * HEIGHT / 4,
                ti.random() * 400
            ]
            self.velocities[i] = [0, 0, 0]
            self.accelerations[i] = [0, 0, 0]
            self.masses[i] = 1

        self.active_bodies[None] = num_bodies

    @ti.kernel
    def compute_gravity(self):
        for i in range(self.active_bodies[None]):
            for j in range(i + 1, self.active_bodies[None]):
                direction = self.positions[j] - self.positions[i]
                distance = direction.norm() + 1e-3  # avoid singularity

                force_magnitude = (
                    self.G * self.masses[i] * self.masses[j]
                ) / (distance * distance)

                force_direction = direction / distance
                force = force_magnitude * force_direction
                
                if force.norm() > 100: # cap the force to prevent numerical instability
                    force = 100 * force_direction

                self.accelerations[i] += force / self.masses[i]
                self.accelerations[j] -= force / self.masses[j]

    @ti.kernel
    def update(self):
        for i in range(self.active_bodies[None]):
            # Euler integration (explizit)
            self.velocities[i] += self.accelerations[i] * self.dt
            self.positions[i] += self.velocities[i] * self.dt

            # reset acceleration
            self.accelerations[i] = [0, 0, 0]

    def physics_step(self):
        self.compute_gravity()
        self.update()
      

sim = Simulation()
sim.init_particles(10000)

class Camera: #3d
    def __init__(self):
        self.position = np.array([0, 0, 0], dtype=np.float32)
        self.yaw = 0
        self.pitch = 0
        self.speed = 250
    
    def update(self, dt, event):
        direction_looking = np.array([
            np.cos(self.pitch) * np.sin(self.yaw),
            np.sin(self.pitch),
            np.cos(self.pitch) * np.cos(self.yaw)
        ], dtype=np.float32)
        right = np.array([
            np.sin(self.yaw - np.pi/2),
            0,
            np.cos(self.yaw - np.pi/2)
        ], dtype=np.float32)
        up = np.cross(right, direction_looking) 
        
        if event == 'forward':
            self.position += direction_looking * self.speed * dt
        if event == 'backward':
            self.position -= direction_looking * self.speed * dt
        if event == 'left':
            self.position -= right * self.speed * dt
        if event == 'right':
            self.position += right * self.speed * dt
        if event == 'up':
            self.position += up * self.speed * dt
        if event == 'down':
            self.position -= up * self.speed * dt
    
    def get_view_matrix(self):
        direction_looking = glm.vec3(
            np.cos(self.pitch) * np.sin(self.yaw),
            np.sin(self.pitch),
            np.cos(self.pitch) * np.cos(self.yaw)
        )
        direction_looking = glm.normalize(direction_looking) #normalizing the direction vector
        target = self.position + direction_looking
        up = np.array([0, 1, 0], dtype=np.float32)
        return glm.lookAt(glm.vec3(*self.position), glm.vec3(*target), glm.vec3(*up))
    
    def get_projection_matrix(self):
        aspect_ratio = WIDTH / HEIGHT
        return glm.perspective(glm.radians(45), aspect_ratio, 0.1, 10000.0)

camera = Camera()

class Input:
    def __init__(self):
        self.mouse_pos = (0, 0)
        self.mouse_pressed = False
        self.sensitivity = 0.002
        self.locked = True
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        pygame.mouse.get_rel() #reset mouse movement to prevent jumps on first frame
    
    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_pressed = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.locked = not self.locked
                    pygame.event.set_grab(self.locked)
                    pygame.mouse.set_visible(not self.locked)
                    pygame.mouse.get_rel()
                if event.key == pygame.K_0:
                    sim.positions.fill(0)
                    sim.velocities.fill(0)
                    sim.accelerations.fill(0)
                    sim.active_bodies[None] = 0
                    sim.init_particles(10000)


        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            camera.update(sim.dt, 'forward')
        if keys[pygame.K_s]:
            camera.update(sim.dt, 'backward')
        if keys[pygame.K_a]:
            camera.update(sim.dt, 'left')
        if keys[pygame.K_d]:
            camera.update(sim.dt, 'right')
        if keys[pygame.K_SPACE]:
            camera.update(sim.dt, 'up')
        if keys[pygame.K_LSHIFT]:
            camera.update(sim.dt, 'down')
        if keys[pygame.K_LCTRL]:
            camera.speed = 2000
        if not keys[pygame.K_LCTRL]:
            camera.speed = 250
            
        if not self.locked:
            return
        
        pygame.mouse.set_pos(WIDTH // 2, HEIGHT // 2)
                    
        #self.mouse_pos = pygame.mouse.get_pos()
        dx, dy = pygame.mouse.get_rel()
        camera.yaw -= dx * self.sensitivity
        camera.pitch -= dy * self.sensitivity
        limit = np.radians(89)
        camera.pitch = max(-limit, min(limit, camera.pitch))

input_handler = Input()

class Renderer:
    def __init__(self):
        self.prog = ctx.program(
            vertex_shader='''
                #version 330
                in vec3 in_position;
                uniform mat4 view;
                uniform mat4 projection;
                void main() {
                    vec4 viewPos = view * vec4(in_position, 1.0);
                    gl_Position = projection * viewPos;
                    gl_PointSize = clamp(1000.0 / -viewPos.z, 0.1, 10.0);
                }
            ''',
            fragment_shader='''
                #version 330

        out vec4 fragColor;

        void main() {
            vec2 coord = gl_PointCoord - vec2(0.5);
            float dist = length(coord);

            if (dist > 0.5)
                discard;

            float core = 1.0 - smoothstep(0.0, 0.1, dist);
            float glow = 1.0 - smoothstep(0.0, 0.5, dist);

            vec3 coreColor = vec3(1.0);
            vec3 glowColor = vec3(0.3, 0.6, 1.0);

            vec3 color = mix(glowColor, coreColor, core);

            fragColor = vec4(color, glow);
        }
            '''
        )
        self.vbo = ctx.buffer(reserve=sim.max_bodies * 12)
        self.positions_np = np.empty((sim.max_bodies, 3), dtype=np.float32)
        self.vao = ctx.simple_vertex_array(self.prog, self.vbo, 'in_position')
    
    def render(self):
        self.positions_np[:] = sim.positions.to_numpy()
        self.vbo.orphan()
        self.vbo.write(self.positions_np.tobytes())
        self.prog['view'].write(camera.get_view_matrix().to_bytes())
        self.prog['projection'].write(camera.get_projection_matrix().to_bytes())
        ctx.clear(0, 0, 0)
        self.vao.render(mode=moderngl.POINTS)

renderer = Renderer()
        
if __name__ == "__main__":
    while True:
        input_handler.update()
        sim.physics_step()
        renderer.render()
        
        pygame.display.flip()