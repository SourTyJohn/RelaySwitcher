from Serial import SerialAPI


class CompileError(SyntaxError):
    pass


class CodeAPI:
    def __init__(self, ):
        self.code = []
        self.curr_line = 0
        self.lines = len(self.code)
        self.curr_delay = 0
        self.delay = 0
        self.curr_repeat = 0
        self.repeat = 0

        self.time = 0

    def compile(self, lines):
        if not lines:
            self.code = []
            return

        compiled_lines = []

        rep_start = "-"
        for i, line in enumerate(lines):
            line = line.strip().lower()
            tokens = line.split(" ")
            if line:
                match tokens[0]:
                    case "rep":
                        line = "R " + tokens[1]
                        rep_start = str(i)
                    case "endr":
                        if rep_start == "-":
                            raise CompileError
                        line = "E " + rep_start
                    case "delays":
                        line = "D " + str(int(tokens[1]) * 1000)
                    case "delaym":
                        line = "D " + str(int(tokens[1]) * 60 * 1000)
                    case "delayh":
                        line = "D " + str(int(tokens[1]) * 60 * 60 * 1000)

                if line[0] != "s" and line[0] != '0' and line[0].isdigit():
                    line = 's' + ''.join( [
                        str( int(x) * 2 - 1) + str( int(x) * 2 ) for x in line]
                    )

                compiled_lines.append(line)

        self.code = compiled_lines
        self.curr_line = 0
        self.lines = len(self.code)
        self.curr_delay = 0
        self.delay = 0
        self.curr_repeat = 0
        self.repeat = 0

        self.time = 0

        print("CODE:")
        print(self.code)

    def step(self, dt, paused):
        if paused:
            return self.curr_line, "PAUSED"

        if not self.code:
            return self.curr_line, "NO_CODE"

        self.time += dt

        if self.curr_delay >= self.delay:
            self.curr_delay = 0
            self.delay = 0
        else:
            self.curr_delay += dt
            return self.curr_line, "WAIT"

        if self.curr_line == self.lines:
            return self.curr_line, "FINISHED"

        line = self.code[self.curr_line]
        tokens = line.split()

        flag = False
        match tokens[0]:
            case "R":
                self.curr_repeat = 1
                self.repeat = int(tokens[1])
                flag = True
            case "E":
                if self.curr_repeat != self.repeat:
                    self.curr_repeat += 1
                    self.curr_line = int(tokens[1])
                flag = True
            case "D":
                self.delay = int(tokens[1])
                flag = True

        self.curr_line += 1

        if flag is False:
            SerialAPI.sendLine( line + '\n\r' )
            return self.curr_line, line
        return self.curr_line, "NONE"
