
import random
import StringIO

from gluon.html import *
from gluon.storage import Storage

from Captcha.Visual import Text, Backgrounds, ImageCaptcha
from Captcha import Words


class PseudoGimpy(ImageCaptcha):
    """A relatively easy CAPTCHA that's somewhat easy on the eyes"""
    def getLayers(self):
        word = Words.defaultWordList.pick()
        self.addSolution(word)
        return [           
            random.choice([    
                Backgrounds.CroppedImage(),
                Backgrounds.TiledImage(),
            ]),                
            Text.TextLayer(word, borderSize=1)
        ]

    def base64(self):
        """Render a tag with image data
        """
        img = self.render()
        output = StringIO.StringIO()
        img.save(output, 'PNG')
        contents = output.getvalue().encode('base64')
        output.close()
        return 'data:image/png;base64,' + contents


class Captcha(DIV):
    def __init__(
        self,
        request,
        session,
        error=None,
        error_message='invalid',
        label='Type the text:',
        options='',
        comment = '',
    ):
        self.request_vars = request.vars
        self.session = session
        self.error = error
        self.errors = Storage()
        self.error_message = error_message
        self.components = []
        self.attributes = {}
        self.label = label
        self.options = options
        self.comment = comment

    def _validate(self):
        """Check result
        """
        recaptcha_response_field = self.request_vars.recaptcha_response_field
        #recaptcha_challenge_field = self.request_vars.recaptcha_challenge_field
        recaptcha_challenge_field = self.session.recaptcha_challenge_field
        if not (recaptcha_response_field and recaptcha_challenge_field):
            self.errors['captcha'] = self.error_message
            return False
        if recaptcha_challenge_field == recaptcha_response_field:
            del self.request_vars.recaptcha_response_field
            #del self.request_vars.recaptcha_challenge_field
            del self.session.recaptcha_challenge_field
            self.request_vars.captcha = ''
            return True
        else:
            # incorrect result
            self.errors['captcha'] = self.error_message

    def xml(self):
        error_param = ''
        if self.error:
            error_param = '&error=%s' % self.error

        # Generate a CAPTCHA
        g = PseudoGimpy()
        captcha = DIV(
            IMG(_src=g.base64()),
            BR(),
            INPUT(_name='recaptcha_response_field'), 
            #INPUT(_type='hidden', _name='recaptcha_challenge_field', _value=g.solutions[0]), 
            _id='recaptcha'
        )
        self.session.recaptcha_challenge_field = g.solutions[0]

        if self.errors.captcha:
            captcha.append(DIV(self.errors['captcha'], _class='error'))
        return XML(captcha).xml()
