FROM amazonlinux

ENV PYTHONUNBUFFERED=1

RUN yum update -y
RUN yum upgrade -y
RUN yum groupinstall "Development Tools" -y
RUN yum install python3-devel -y
RUN yum install python3-pip -y

COPY fortuna_extras fortuna_extras

RUN python3 -m venv venv
ENV PATH="/venv/bin:$PATH"
RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip install Fortuna[scope]

CMD python -i -m fortuna_extras.fortuna_tests
