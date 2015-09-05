
from teaching_rdfizer import pickProperLabel

if __name__ == "__main__":
    nom = "R.M."
    cognom = "Gil"
    print "Proper label is {}".format(pickProperLabel(nom, cognom))

    nom = "M.T."
    cognom = "Alsinet"
    print "Proper label is {}".format(pickProperLabel(nom, cognom))
