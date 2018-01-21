from BisonInput import ButtonChain
import time
if __name__ == "__main__":
    myChain = ButtonChain(frequency=2000, cycles = 66, didOffset = 2)

        # self.buttonChain = ButtonChain(
        #     frequency=2500,
        #     cycles = 8,
        #     didOffset = 2,
        #     onPress = self.onPress,
        #     onUnPress = self.onUnPress)


    myChain.run()
