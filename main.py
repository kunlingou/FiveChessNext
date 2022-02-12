#__u
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import json
from collections import defaultdict
import random
import pygame
import heapq

INVALID_ACTION = (-1, -1)

STONE_BLANK = 0
STONE_BLACK = 1
STONE_WHITE = 2

STONE_INFO = [
    {},
    {
        "name": "黑方",
        "color": (0, 0, 0)
    },
    {
        "name": "白方",
        "color": (255, 255, 255)
    }
]

SPEC_WIDTH = 9
SPEC_HEIGHT = 9

STONE_SIZE = 100
STONE_RADIUS = 20

BUTTON_WIDTH = 100
BUTTON_HEIGHT = 40

BUTTON_TITLE_START = "重新开始"
BUTTON_TITLE_CALC = "智能分析"

INFO_PADDING = 50

COLOR_WHITE = (255, 255, 255)
INFO_COLOR = COLOR_WHITE


MAP_WIDTH = SPEC_WIDTH * STONE_SIZE
INFO_WIDTH = INFO_PADDING * 2 + BUTTON_WIDTH

SCREEN_WIDTH = MAP_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = SPEC_HEIGHT * STONE_SIZE


class Button:

    def __init__(self, name, pos):
        self.rect = pygame.Rect(pos[0], pos[1], BUTTON_WIDTH, BUTTON_HEIGHT)
        self.name = name

    def draw(self, screen):
        screen.fill((26, 173, 25), self.rect)

        msg_image = pygame.font.SysFont("SimHei", BUTTON_HEIGHT * 3 // 5).render( self.name, True, (255, 255, 255), (26, 173, 25))
        msg_image_rect = msg_image.get_rect()
        msg_image_rect.center = self.rect.center
        screen.blit(msg_image, msg_image_rect)

    def click(self, env):
        if self.name == BUTTON_TITLE_START:
            env.start()
        elif self.name == BUTTON_TITLE_CALC:

            agent1 = Agent(env, env.cur_round)
            agent2 = Agent(env, env.get_next_round())

            agent1.mock_and_learn(agent2, 10000, 3)

            state = agent1.reset()
            actions = agent1.get_next_actions(state)

            actions = heapq.nlargest(3, actions, key=lambda k: agent1.get_profit(state, k))

            env.next_actions = []

            for action in actions:
                env.next_actions.append({
                    "pos": action,
                    "profit": agent1.get_profit(state, action)
                })

            with open("learn_map.json", "w") as f:
                f.write(json.dumps({"agent1": agent1.learn_map, "agent2": agent2.learn_map}))


class Environment:

    def __init__(self, config):
        self.width = config["width"]
        self.height = config["height"]
        print(f'Hi, {json.dumps(self.__dict__)}')
        self.game_state = 0
        self.stones = 0
        self.cur_round = 0
        self.next_actions = 0

        self.buttons = [
            Button(BUTTON_TITLE_START, (MAP_WIDTH + INFO_PADDING, INFO_PADDING)),
            Button(BUTTON_TITLE_CALC, (MAP_WIDTH + INFO_PADDING, INFO_PADDING + BUTTON_HEIGHT + INFO_PADDING))
        ]

        pygame.init()
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption("FIVE CHESS NEXT")
        self.clock = pygame.time.Clock()

        self.start()

    def start(self):
        self.game_state = 0
        self.stones = defaultdict(int)
        self.cur_round = STONE_BLACK
        self.next_actions = []

    def play(self):
        self.clock.tick(60)

        # 背景颜色

        pygame.draw.rect(self.screen, (247, 238, 214), pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(MAP_WIDTH, 0, INFO_WIDTH, SCREEN_HEIGHT))

        # 棋盘线条

        for i in range(self.height):
            line_width = 2 if i == self.height // 2 else 1
            height = STONE_SIZE / 2 + i * STONE_SIZE
            pygame.draw.line(self.screen, (0, 0, 0), (STONE_SIZE / 2, height), (STONE_SIZE / 2 + (self.width - 1) * STONE_SIZE, height), line_width)

        for i in range(self.width):
            line_width = 2 if i == self.width // 2 else 1
            width = STONE_SIZE / 2 + i * STONE_SIZE
            pygame.draw.line(self.screen, (0, 0, 0), (width, STONE_SIZE / 2), (width, STONE_SIZE / 2 + (self.height - 1) * STONE_SIZE), line_width)

        # 按钮

        for button in self.buttons:
            button.draw(self.screen)

        # 游戏结果

        button_rect = pygame.Rect(MAP_WIDTH + INFO_PADDING, INFO_PADDING + BUTTON_WIDTH + INFO_PADDING, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.screen.fill(INFO_COLOR, button_rect)

        if self.game_state:
            msg_image = pygame.font.SysFont("SimHei", BUTTON_HEIGHT * 2 // 4).render(
                "游戏结束，" + STONE_INFO[self.cur_round]["name"] + "胜利", True, (0, 0, 0), (26, 173, 25))
            msg_image_rect = msg_image.get_rect()
            msg_image_rect.center = button_rect.center
            self.screen.blit(msg_image, msg_image_rect)
        else:
            msg_image = pygame.font.SysFont("SimHei", BUTTON_HEIGHT * 2 // 4).render(
                "当前回合:" + STONE_INFO[self.cur_round]["name"], True, (0, 0, 0), (26, 173, 25))
            msg_image_rect = msg_image.get_rect()
            msg_image_rect.center = button_rect.center
            self.screen.blit(msg_image, msg_image_rect)

        # 分析结果

        button_rect = pygame.Rect(MAP_WIDTH + INFO_PADDING, INFO_PADDING + BUTTON_WIDTH + INFO_PADDING + BUTTON_WIDTH, BUTTON_WIDTH,
                                  BUTTON_HEIGHT)
        self.screen.fill(INFO_COLOR, button_rect)

        result_height = button_rect.center[1]
        for action in self.next_actions:
            cal_result = str(action["pos"]) + " " + str(round(action["profit"], 2))
            msg_image = pygame.font.SysFont("SimHei", BUTTON_HEIGHT * 2 // 4).render(cal_result, True, (0, 0, 0), (26, 173, 25))
            msg_image_rect = msg_image.get_rect()
            msg_image_rect.center = (button_rect.center[0], result_height)
            self.screen.blit(msg_image, msg_image_rect)

            result_height += BUTTON_HEIGHT

        # 棋子

        for k, v in self.stones.items():
            if v == 0:
                continue
            pygame.draw.circle(self.screen, STONE_INFO[v]["color"], ((k[0] + 0.5) * STONE_SIZE, (k[1] + 0.5) * STONE_SIZE), STONE_RADIUS)

    def get_next_round(self):
        return STONE_BLACK + STONE_WHITE - self.cur_round

    def click(self, click_pos):
        print(f"click success, pos: {click_pos}")
        if click_pos[0] <= MAP_WIDTH:
            if self.game_state != 0:
                return

            x = click_pos[0] // STONE_SIZE
            y = click_pos[1] // STONE_SIZE

            self.stones[(x, y)] = self.cur_round

            if self.get_game_result(self.stones, (x, y), self.cur_round):
                self.game_state = self.cur_round
            else:
                self.cur_round = self.get_next_round()

        else:
            for button in self.buttons:
                if button.rect.collidepoint(click_pos):
                    print(f"click button success, pos: {click_pos}")
                    button.click(self)

    def get_game_result(self, state, action, stone_color):
        cur_pos = action

        for pos in [(cur_pos[0], cur_pos[1] - 1), (cur_pos[0] + 1, cur_pos[1] - 1), (cur_pos[0] + 1, cur_pos[1]),
                    (cur_pos[0] + 1, cur_pos[1] + 1), (cur_pos[0], cur_pos[1] + 1), (cur_pos[0] - 1, cur_pos[1] + 1),
                    (cur_pos[0] - 1, cur_pos[1]), (cur_pos[0] - 1, cur_pos[1] - 1)]:
            if 0 <= pos[0] < self.width and 0 <= pos[1] < self.height and state[pos] == stone_color:
                finish_len = 2
                x_offset = pos[0] - cur_pos[0]
                y_offset = pos[1] - cur_pos[1]
                while finish_len < 5:
                    next_pos = (pos[0] + x_offset, pos[1] + y_offset)
                    if state[next_pos] != stone_color:
                        break
                    finish_len += 1
                    pos = next_pos
                if finish_len == 5:
                    return True
        return False


class Agent:

    def __init__(self, env, stone_color):
        self.env = env
        self.stone_color = stone_color
        self.stones = defaultdict(int)
        self.learn_map = {}

        self.learning_rate = 0.01
        self.discount_factor = 0.9
        self.epsilon = 0.01

    def reset(self):
        return self.env.stones.copy()

    def get_next_actions(self, state):
        actions = []
        for x in range(self.env.width):
            for y in range(self.env.height):
                if state[(x, y)] != STONE_BLANK:
                    continue
                actions.append((x, y))
        return actions

    def get_next_action(self, state):
        actions = self.get_next_actions(state)
        if len(actions) == 0:
            return None

        if random.random() <= self.epsilon:
            return heapq.nlargest(1, actions, key=lambda k: self.get_profit(state, k))[0]
        else:
            return random.choice(actions)

    def cal_reward(self, state, action):

        if self.env.get_game_result(state, action, self.stone_color):
            return 100

        return 0

    def mock(self, state, action):

        next_state = state.copy()

        next_state[action] = self.stone_color

        reward = self.cal_reward(next_state, action)

        return reward, next_state

    def get_state_key(self, state):
        key = ""
        for i in range(self.env.width * self.env.height):
            key += str(state[(i % self.env.width, (i + self.env.width - 1) // self.env.width)])
        return key

    def learn(self, state, action, next_state, reward):

        state_key = self.get_state_key(state)
        if not self.learn_map.__contains__(state_key):
            self.learn_map[state_key] = {}

        next_state_key = self.get_state_key(next_state)
        if not self.learn_map.__contains__(next_state_key):
            self.learn_map[next_state_key] = {}

        action_key = str(action[0]) + "_" + str(action[1])
        if not self.learn_map[state_key].__contains__(action_key):
            self.learn_map[state_key][action_key] = 0

        old_profit = self.learn_map[state_key][action_key]

        new_profit = reward + self.discount_factor * max(self.learn_map[next_state_key].values() if len(self.learn_map[next_state_key]) > 0 else [0])

        self.learn_map[state_key][action_key] += self.learning_rate * (new_profit - old_profit)

    def get_profit(self, state, action):
        state_key = self.get_state_key(state)
        action_key = str(action[0]) + "_" + str(action[1])
        if not self.learn_map.__contains__(state_key) or not self.learn_map[state_key].__contains__(action_key):
            return 0
        return self.learn_map[state_key][action_key]

    def print_state(self, state):
        print("\nstate info:")
        for y in range(self.env.height):
            for x in range(self.env.width):
                print(f"{state[(x, y)]} ", end="")
            print("")

    def mock_and_learn(self, agent2, try_times, max_steps):

        for i in range(try_times):
            state = self.reset()

            game_over = 0
            step = 0

            while game_over == 0:

                for agent in [self, agent2]:
                    action = agent.get_next_action(state)

                    if not action:
                        # print(f"{i} game over1")
                        game_over = 1
                        break

                    reward, next_state = agent.mock(state, action)

                    # agent.print_state(next_state)

                    agent.learn(state, action, next_state, reward)

                    if reward == 100:
                        print(f"{i} game over2 action {action}")
                        game_over = 2
                        break

                    step += 1

                    if 0 < max_steps <= step:
                        # print(f"{i} game over3")
                        game_over = 3
                        break

                    state = next_state


def main():

    env = Environment({"width": SPEC_WIDTH, "height": SPEC_HEIGHT})

    while 1:

        env.play()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                env.click(pygame.mouse.get_pos())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('hello GoBang Next')

    main()




