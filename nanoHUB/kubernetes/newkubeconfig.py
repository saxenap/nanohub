#in order to use kube-template.yaml, we encompass all naturally used {} with another set of them to escape the formatting indicator
# {} -> {{}} for non-name references, this is in kube-template

def func():

    kubeConfig = open("kube-template.yaml", "r")
    data = kubeConfig.read()
    kubeConfig.close()

    newUser = "hunte164"
    newData = data.format(newUser)

    newConfig = open("new-kube-config.yaml", "w")
    n = newConfig.write(newData)
    newConfig.close()

if __name__ == "__main__":
    func()