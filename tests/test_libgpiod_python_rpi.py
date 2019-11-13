import RPi.GPIO as GPIO
import pytest
import re
import os

def foo():
    pass

def test_is_all_ints():
    GPIO.Reset()
    invalid_data = ['a', {'a':5}, foo]
    valid_data = [1, [1,2,3,4], 10000]
    for i in invalid_data:
        assert GPIO.is_all_ints(i) == False
    for i in valid_data:
        assert GPIO.is_all_ints(i) == True

def test_is_all_bools():
    GPIO.Reset()
    invalid_data = [foo, None, 5]
    valid_data = [True, False]
    for i in invalid_data:
        assert GPIO.is_all_bools(i) == False
    for i in valid_data:
        assert GPIO.is_all_bools(i) == True

def test_is_iterable():
    GPIO.Reset()
    a = re.compile(r'[\d]+')
    invalid_data = [None, 1, foo, a]
    valid_data = ["a", "iter", [], [1,2,3]]
    for i in invalid_data:
        assert GPIO.is_iterable(i) == False
    for i in valid_data:
        assert GPIO.is_iterable(i) == True

def test_setmode_raise_double_setup_exception():
    GPIO.Reset()
    with pytest.raises(Exception):
        GPIO.setmode(GPIO.BCM)
        GPIO.setmode(GPIO.BOARD)

def test_setmode_raise_invalid_mode_exception():
    GPIO.Reset()
    with pytest.raises(Exception):
        GPIO.setmode(5)
    with pytest.raises(Exception):
        GPIO.setmode('a')
    with pytest.raises(Exception):
        GPIO.setmode([])


def test_getmode():
    GPIO.Reset()
    GPIO.State_Access().mode = GPIO.BOARD
    assert GPIO.getmode() == GPIO.BOARD

    GPIO.State_Access().mode = GPIO.BCM
    assert GPIO.getmode() == GPIO.BCM

    GPIO.State_Access().mode = None
    assert GPIO.getmode() == None

    GPIO.Reset()

def test_validate_pin_or_die():
    GPIO.Reset()
    pass    


def test_setmode():
    GPIO.Reset()

    with pytest.raises(ValueError):
        GPIO.setmode(23)

    GPIO.setmode(GPIO.BCM)

    with pytest.raises(ValueError):
        GPIO.setmode(GPIO.BOARD)

    with pytest.raises(ValueError):
        GPIO.setmode(GPIO.UNKNOWN)

    GPIO.Reset()
    # Cannot use this yet
    # with os.setuid(1):
    #     GPIO.setmode(GPIO.BCM)


def test_set_warnings():
    GPIO.Reset()

    GPIO.setwarnings(True)
    assert GPIO.State_Access().warnings == True

    GPIO.setwarnings(False)
    assert GPIO.State_Access().warnings == False

def test_setup():
    GPIO.Reset()

    GPIO.setmode(GPIO.BCM)

    with pytest.raises(ValueError) as e:
        GPIO.setup("foo", "bar")
    assert "Channel must be an integer" in str(e.value)

    with pytest.raises(ValueError) as e:
        GPIO.setup("foo", GPIO.OUT) 
    assert "Channel must be an integer" in str(e.value)

    with pytest.raises(ValueError) as e:
        GPIO.setup(["foo", "bar"], GPIO.OUT) 
    assert "Channel must be an integer" in str(e.value)

    with pytest.raises(ValueError) as e:
        GPIO.setup([1, "bar"], GPIO.OUT) 
    assert "Channel must be an integer" in str(e.value)

    with pytest.raises(ValueError) as e:
        GPIO.setup(54, GPIO.OUT)
    assert "channel sent is invalid" in str(e.value)

    with pytest.raises(ValueError) as e:
        GPIO.setup(666, GPIO.OUT)
    assert "channel sent is invalid" in str(e.value)

    with pytest.raises(ValueError) as e:
        GPIO.setup(-1, GPIO.OUT)
    assert "channel sent is invalid" in str(e.value)

    with pytest.raises(ValueError) as e:
        GPIO.setup(23, -666)     # Shoutout to RPi.GPIO magic numbers
    assert "invalid direction was passed" in str(e.value)

    with pytest.raises(ValueError) as e:
        GPIO.setup(18, GPIO.OUT, GPIO.PUD_UP)
    assert "pull_up_down parameter is not valid for outputs" in str(e.value)

    with pytest.raises(ValueError) as e:
        GPIO.setup(18, GPIO.IN, -666)
    assert "Invalid value for pull_up_down" in str(e.value)

    GPIO.setup(18, GPIO.IN, GPIO.PUD_UP)

    with pytest.warns(Warning) as w:
        GPIO.setup([16,17,18], GPIO.OUT)
    assert "already in use" in str(w[0].message)

    with pytest.raises(ValueError) as e:
        GPIO.setup(2, GPIO.IN, GPIO.PUD_OFF, 1)
    assert "initial parameter is not valid for inputs" in str(e.value)

    GPIO.setup([2,3,4], GPIO.OUT)

    # Ensure line objects for those pins were successfully created
    assert all([pin in GPIO.State_Access().lines.keys() for pin in [2,3,4]])



def test_output():
    GPIO.Reset()
    GPIO.setmode(GPIO.BCM)
    chans = [16,17,18]

    GPIO.setup(chans, GPIO.OUT)

    GPIO.output(chans, [1,0,1])

    GPIO.Reset()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(chans, GPIO.OUT)

    # Make sure the simple case works
    GPIO.output(16, 1)

    with pytest.raises(ValueError) as e:
        GPIO.output("foo", "bar")
    assert "Channel must be an integer or list/tuple of integers" in str(e.value)

    with pytest.raises(ValueError) as e:
        GPIO.output([16, "foo"], 1)
    assert "Channel must be an integer or list/tuple of integers" in str(e.value)

    with pytest.raises(ValueError) as e:
        GPIO.output(16, [])
    assert "Value must be an integer/boolean or a list/tuple of integers/booleans" in str(e.value)

    with pytest.warns(Warning) as w:
        GPIO.output(19, 1)
    assert "channel has not been set up as an OUTPUT" in str(w[0].message)

    # Also might be worth triggering the error condition
    # Not sure how to do this without having a second process use a gpio port

    # TODO: why does this raise a different exception than expected?
    # with pytest.raises(RuntimeError):
    #     GPIO.output(chans, [1,0,0,1])
    # assert "Number of channel != number of value" in str(e.value)


    # Other tests
    GPIO.Reset()
    with pytest.raises(Exception):
        GPIO.setup([1,2,3], GPIO.OUT)
        GPIO.output([1,2,3],[1,2,3,4])
    with pytest.raises(Exception):
        GPIO.output([],[])

    GPIO.Reset()

def test_input():
    GPIO.Reset()
    GPIO.setmode(GPIO.BCM)


    chans = [16,17,18]

    GPIO.setup(chans, GPIO.IN)

    # Invalid input
    with pytest.raises(ValueError) as e:
        GPIO.input(chans)
    assert "channel sent is invalid" in str(e.value)

    # Can't really do anything more complicated with pure software
    GPIO.input(16)

def test_wait_for_edge():
    GPIO.Reset()
    GPIO.setmode(GPIO.BCM)

    # This only works in our impementation. RPi.GPIO requires
    # one to setup the pin as an input first.
    GPIO.wait_for_edge(16, GPIO.BOTH_EDGE, 1, 1)

    # A quirk of our workaround is that a later attempt to setup the pin
    # will result in a warning, despite there being no other call to
    # setup(16)
    with pytest.warns(Warning) as w:
        GPIO.setup(16, GPIO.IN)
    assert "already in use" in str(w[0].message)
    # And subsequent calls to wait_for_edge will succeed just fine
    GPIO.wait_for_edge(16, GPIO.BOTH_EDGE)

    GPIO.Reset()
    GPIO.setmode(GPIO.BCM)
    with pytest.raises(ValueError) as e:
        GPIO.wait_for_edge(16, 666)
    assert "edge must be set" in str(e.value)

    # Bouncetime > 0
    with pytest.raises(ValueError) as e:
        GPIO.wait_for_edge(16, GPIO.RISING_EDGE, 0)
    assert "Bouncetime must be" in str(e.value)

    # Timeout >= 0
    with pytest.raises(ValueError) as e:
        GPIO.wait_for_edge(16, GPIO.RISING_EDGE, timeout=-1)
    assert "Timeout must be" in str(e.value)

    # TODO We cannot test for the (Device or Resoruce Busy) exeption without another thread/process

def test_add_event_detect():
    GPIO.Reset()
    GPIO.setmode(GPIO.BCM)

    with pytest.raises(ValueError) as e:
        GPIO.add_event_detect(16, 47)
    assert "edge must be set" in str(e.value)

    with pytest.raises(TypeError) as e:
        GPIO.add_event_detect(16, GPIO.FALLING_EDGE, "foo")
    assert "Parameter must be callable" in str(e.value)

    # Bouncetime > 0
    with pytest.raises(ValueError) as e:
        GPIO.add_event_detect(16, GPIO.RISING_EDGE, bouncetime=-1)
    assert "Bouncetime must be" in str(e.value)

    GPIO.add_event_detect(16, GPIO.FALLING_EDGE, foo, 1)
    GPIO.add_event_detect(17, GPIO.FALLING_EDGE, bouncetime=1)
    GPIO.Reset()

def test_add_event_callback():
    GPIO.Reset()
    GPIO.setmode(GPIO.BCM)

    GPIO.add_event_detect(17, GPIO.FALLING_EDGE, bouncetime=1)

    with pytest.raises(RuntimeError) as e:
        GPIO.add_event_callback(16, foo)
    assert "Add event detection using add_event_detect first" in str(e.value)
    
    with pytest.raises(TypeError) as e:
        GPIO.add_event_callback(17, "foo")
    assert "Parameter must be callable" in str(e.value)

    GPIO.add_event_callback(17, foo)
    GPIO.Reset()
    
def test_remove_event_detect():
    GPIO.Reset()
    GPIO.setmode(GPIO.BCM)

    GPIO.add_event_detect(17, GPIO.FALLING_EDGE, bouncetime=1)
    GPIO.add_event_callback(17, foo)

    GPIO.remove_event_detect(17)

    with pytest.raises(ValueError) as e:
        GPIO.remove_event_detect(16)
    assert "event detection not setup" in str(e.value)

def test_event_detected():
    GPIO.Reset()
    GPIO.setmode(GPIO.BCM)

    GPIO.add_event_detect(18, GPIO.FALLING_EDGE, bouncetime=1)
    GPIO.event_detected(18)
    
    assert GPIO.event_detected(18) == False

    # Manufacture a false positive
    GPIO.State_Access().event_ls.append(18)
    assert GPIO.event_detected(18) == True

    GPIO.Reset()


def test_gpio_function():
    GPIO.Reset()
    GPIO.setmode(GPIO.BCM)

    assert GPIO.gpio_function(16) == 16

    GPIO.Reset()
    GPIO.setmode(GPIO.BOARD)
    
    assert GPIO.gpio_function(16) == 11