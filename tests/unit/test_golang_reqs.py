from deltaver.golang_reqs import GolangReqs


def test_version_number():
    got = GolangReqs('\n'.join([
        'filippo.io/edwards25519 v1.1.0 h1:FNf4tywRC1HmFuKW5xopWpigGjJKiJSV0Cqo0cJWDaA=',
        'filippo.io/edwards25519 v1.1.0/go.mod h1:BxyFTGdWcka3PhytdK4V28tE5sGfRvvvRV7EaN4VDT4=',
    ])).reqs()

    assert got == [('filippo.io/edwards25519', 'v1.1.0')]


def test_last_version():
    got = GolangReqs('\n'.join([
        'github.com/aws/aws-sdk-go-v2 v1.38.1 h1:j7sc33amE74Rz0M/PoCpsZQ6OunLqys/m5antM0J+Z8=',
        'github.com/aws/aws-sdk-go-v2 v1.38.1/go.mod h1:9Q0OoGQoboYIAJyslFyF1f5K1Ryddop8gqMhWx/n4Wg=',
        'github.com/aws/aws-sdk-go-v2 v1.38.0 h1:UCRQ5mlqcFk9HJDIqENSLR3wiG1VTWlyUfLDEvY7RxU=',
        'github.com/aws/aws-sdk-go-v2 v1.38.0/go.mod h1:9Q0OoGQoboYIAJyslFyF1f5K1Ryddop8gqMhWx/n4Wg=',
    ])).reqs()

    assert got == [('github.com/aws/aws-sdk-go-v2', 'v1.38.1')]
